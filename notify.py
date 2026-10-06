#!/usr/bin/env python3
"""Annonce sur Discord les besoins internes publiés, et relance ceux que personne ne prend.

Le job interroge Notion, il n'attend aucun appel entrant. Trois messages :
  - annonce : un besoin est en État = Publication et n'a pas encore été annoncé
  - relance : un besoin publié depuis RELANCE_APRES_JOURS jours n'a toujours pas
    d'Owner — répétée tous les RELANCE_INTERVALLE_JOURS jours jusqu'à ce qu'il en ait un
  - rappel de pré-validation : un besoin attend en État = Pré-validation depuis
    RAPPEL_PREVALIDATION_JOURS jours — répété au même rythme tant qu'il y reste
    (autre channel)

Toute la mémoire vit dans Notion (case « Annoncé sur Discord », dates « Dernière
relance Discord » et « Dernier rappel pré-validation »), jamais ici. Le job peut donc tourner en double, planter et redémarrer
sans jamais poster deux fois la même chose — et l'état reste lisible à l'œil dans
la base.

Variables d'environnement :
  NOTION_TOKEN                token d'une intégration interne Notion
  NOTION_DATABASE_ID          id de « Base des besoins internes »
  NOTION_CANDIDATURES_DB_ID   id de « Base de candidatures à un besoin »
  DISCORD_WEBHOOK_URL         webhook entrant du channel dédié
  DISCORD_WEBHOOK_PREVALIDATION_URL
                              webhook du channel des rappels de pré-validation ;
                              optionnel, son absence désactive seulement ces rappels
  NOTION_DESTAFF_DB_ID        id de « Demandes de destaff et d'intercontrat » ;
                              optionnel, son absence désactive seulement ce volet
  DRY_RUN                     à 1, affiche ce qui partirait sans rien poster ni écrire
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date

# L'API Notion versionne par date. 2022-06-28 expose /databases/{id}/query, stable
# et largement documenté ; les versions 2025+ passent par /data_sources/{id}/query.
NOTION_VERSION = "2022-06-28"
NOTION_API = "https://api.notion.com/v1"

# Exigé par Discord (voir post_discord). Un agent générique se fait rejeter par Cloudflare.
USER_AGENT = "RegistreBesoinsCB/1.0 (+https://github.com/Code-Busters-Internal/registre-besoins-cb)"

# Un besoin publié est relancé tant qu'il n'a pas d'Owner, sans limite de durée : un
# besoin publié et sans porteur est un besoin en souffrance, il doit rester visible.
RELANCE_APRES_JOURS = 10  # âge minimum d'un besoin publié pour être relancé
RELANCE_INTERVALLE_JOURS = 10  # écart minimum entre deux relances d'un même besoin

# Ne comptent pas comme un candidat :
#  - « Brouillon » : le bouton « Candidater » crée la candidature dans cet état, elle ne
#    vaut qu'une fois validée par son auteur ;
#  - « Décliné » : le déposant a refusé, donc le besoin cherche toujours quelqu'un — c'est
#    précisément un cas où la relance est utile.
# « Intéressé » et « Retenu » comptent : quelqu'un est sur le coup.
STATUTS_IGNORES = {"Brouillon", "Décliné"}

# Le lien posté mène à la page du besoin, pas à la page d'accueil du registre : c'est
# l'URL que Notion expose et c'est aussi celle que Valmon partage à la main. Or cette
# page ouvre sur une vingtaine de propriétés — un mode d'emploi placé dans son corps
# serait sous la ligne de flottaison. La procédure voyage donc avec le lien.
PROCEDURE = (
    "Clique sur **Candidater** sur la page, puis écris ta **Motivation** : "
    "c'est elle qui valide ta candidature et prévient le déposant. "
    "Sans motivation, elle reste un brouillon que personne ne voit."
)

# « Objectif » a été renommé « Le besoin en une phrase » le 2026-09-08. Le job tournant
# depuis GitHub Actions, le code déployé et le schéma Notion ne changent jamais au même
# instant : on lit donc les deux noms, ce qui rend la migration insensible à l'ordre.
# L'ancien nom pourra être retiré une fois le renommage confirmé en prod.
PROP_PHRASE = "Le besoin en une phrase"
PROP_PHRASE_AVANT_20260908 = "Objectif"

# Ajouté le 2026-09-08 : tout besoin publié ne cherche pas forcément des contributeurs.
# On ne se tait QUE sur un « Non » explicite — une valeur vide garde le comportement
# d'avant (annonce + relance), pour ne pas rendre muets les besoins déjà en base.
PROP_CONTRIBUTEURS = "Besoin de contributeurs"

# Un besoin déposé reste en Pré-validation tant que le responsable de sa catégorie
# (prévenu par e-mail au dépôt) n'a pas statué. Passé ce délai, on le rappelle, puis
# de nouveau à chaque fois que ce même délai s'écoule, tant qu'il y reste.
RAPPEL_PREVALIDATION_JOURS = 5

# Un message Discord est plafonné à 2000 caractères ; on découpe la liste en dessous.
DISCORD_MAX_CARACTERES = 1900

PROP_ANNONCE = "Annoncé sur Discord"
PROP_DERNIERE_RELANCE = "Dernière relance Discord"
PROP_PUBLICATION = "Date de publication"
PROP_DERNIER_RAPPEL_PREVALIDATION = "Dernier rappel pré-validation"
PROP_PREVALIDATION_DEPUIS = "En pré-validation depuis"
PROP_OWNER = "Owner"
PROP_MOTIF_REJET = "Motif de rejet"

# Base « Demandes de destaff et d'intercontrat ». Le job ne fait qu'avancer le Statut
# selon les dates et poser la date de relance : ce sont des automatisations Notion,
# déclenchées par ces écritures, qui envoient les mails (bilan à remplir, relance).
# Notion ne sait pas déclencher une automatisation sur l'arrivée d'une date, d'où ce job.
RELANCE_BILAN_JOURS = 7
DESTAFF_STATUT = "Statut"
DESTAFF_DEBUT = "Date de début"
DESTAFF_FIN = "Date de fin"
DESTAFF_TERMINE_LE = "Terminé le"
DESTAFF_RELANCE = "Relance bilan"
DESTAFF_JOURNAL = "Avancement"
DESTAFF_MOTIF_REFUS = "Motif de refus"

DRY_RUN = os.environ.get("DRY_RUN") == "1"


class ConfigError(RuntimeError):
    pass


def env(name):
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"variable d'environnement manquante : {name}")
    return value


def sans_tirets(identifiant):
    return (identifiant or "").replace("-", "")


def notion_request(method, path, token, payload=None):
    request = urllib.request.Request(
        f"{NOTION_API}{path}",
        method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"Notion {method} {path} → {error.code} : {detail}") from error


def pages_de_base(token, database_id, payload_base=None):
    """Toutes les pages d'une base, pagination comprise."""
    pages = []
    cursor = None
    while True:
        payload = dict(payload_base or {})
        if cursor:
            payload["start_cursor"] = cursor
        data = notion_request("POST", f"/databases/{database_id}/query", token, payload)
        pages.extend(data["results"])
        if not data.get("has_more"):
            return pages
        cursor = data["next_cursor"]


def besoins_dans_etat(token, database_id, etat):
    return pages_de_base(
        token, database_id, {"filter": {"property": "État", "select": {"equals": etat}}}
    )


def index_candidatures(token, database_id):
    """{id du besoin (sans tirets): nombre de candidatures hors brouillon}.

    La base des besoins n'expose aucune relation vers les candidatures : `Besoin` est
    une relation à sens unique, portée par la base des candidatures. Aucun rollup ne
    peut donc compter les candidats depuis le besoin — un « Nb intéressés » avait été
    tenté, il renvoyait null en permanence et a été retiré le 2026-08-10. On agrège
    donc ici, ce qui permet en plus d'exclure les brouillons.
    """
    index = {}
    for page in pages_de_base(token, database_id):
        props = page["properties"]
        if nom_select(props.get("Statut")) in STATUTS_IGNORES:
            continue
        for lien in props.get("Besoin", {}).get("relation", []):
            cle = sans_tirets(lien.get("id"))
            index[cle] = index.get(cle, 0) + 1
    return index


def texte_titre(prop):
    return "".join(part["plain_text"] for part in (prop or {}).get("title", [])).strip()


def texte_riche(prop):
    return "".join(part["plain_text"] for part in (prop or {}).get("rich_text", [])).strip()


def coche(prop):
    return bool((prop or {}).get("checkbox"))


def nom_select(prop):
    select = (prop or {}).get("select")
    return select.get("name", "") if select else ""


def date_debut(prop):
    """Le `start` d'une propriété date, en objet date, ou None."""
    valeur = (prop or {}).get("date")
    if not valeur or not valeur.get("start"):
        return None
    return date.fromisoformat(valeur["start"][:10])


def cocher(token, page_id, propriete):
    if DRY_RUN:
        print(f"    [dry-run] cocherait « {propriete} »")
        return
    notion_request(
        "PATCH",
        f"/pages/{page_id}",
        token,
        {"properties": {propriete: {"checkbox": True}}},
    )


def a_une_relation(prop):
    return bool((prop or {}).get("relation"))


def envoi_du(props, prop_dernier, intervalle, aujourdhui):
    """Vrai si aucun message n'est parti pour cette page depuis `intervalle` jours."""
    dernier = date_debut(props.get(prop_dernier))
    return dernier is None or (aujourdhui - dernier).days >= intervalle


def ecrire_date(token, page_id, propriete, jour):
    if DRY_RUN:
        print(f"    [dry-run] ecrirait « {propriete} » = {jour}")
        return
    notion_request(
        "PATCH",
        f"/pages/{page_id}",
        token,
        {"properties": {propriete: {"date": {"start": jour.isoformat()}}}},
    )


def ecrire_select(token, page_id, propriete, valeur):
    if DRY_RUN:
        print(f"    [dry-run] passerait « {propriete} » à {valeur}")
        return
    notion_request(
        "PATCH",
        f"/pages/{page_id}",
        token,
        {"properties": {propriete: {"select": {"name": valeur}}}},
    )


def titre_page(props):
    """Le titre d'une page, quel que soit le nom de sa propriété titre."""
    for prop in props.values():
        if prop.get("type") == "title":
            return texte_titre(prop) or "(sans titre)"
    return "(sans titre)"


def appliquer_nogos(token, database_id):
    """Passe en Rejeté les besoins en No-go dont le Motif de rejet est rempli.

    Un No-go sans motif n'est jamais appliqué : le déposant doit savoir pourquoi pour
    pouvoir corriger et redéposer. Notion ne sait pas tester un champ texte vide dans
    une automatisation, d'où ce job ; l'automatisation Notion du No-go se contente de
    prévenir le validateur que le motif est obligatoire. Le passage en Rejeté
    déclenche ensuite l'automatisation Notion qui envoie le motif au déposant.
    """
    besoins = pages_de_base(
        token,
        database_id,
        {
            "filter": {
                "and": [
                    {"property": "Décision", "select": {"equals": "No-go"}},
                    {"property": "État", "select": {"equals": "Pré-validation"}},
                ]
            }
        },
    )
    rejetes = 0
    for page in besoins:
        props = page["properties"]
        nom = texte_titre(props.get("Nom")) or "(sans titre)"
        if not texte_riche(props.get(PROP_MOTIF_REJET)):
            print(f"  · No-go sans motif, laissé en Pré-validation : {nom}")
            continue
        ecrire_select(token, page["id"], "État", "Rejeté")
        rejetes += 1
        print(f"  → rejeté : {nom}")
    return rejetes


def avancer_destaffs(token, database_id, aujourdhui):
    """Fait avancer les demandes de destaff et d'intercontrat selon leurs dates.

    - Demande en No-go → Refusé, seulement une fois le Motif de refus rempli ;
    - Demande validée → En cours, dès la date de début ;
    - En cours → Terminé, le lendemain de la date de fin (un intercontrat sans date de
      fin reste En cours : c'est le Buster qui le clôt à la main) ;
    - Terminé depuis RELANCE_BILAN_JOURS jours sans entrée d'avancement → date « Relance bilan »,
      posée une seule fois.

    Les mails partent des automatisations Notion qui écoutent ces propriétés. La base
    étant petite, on la lit en entier plutôt que de filtrer côté API.
    """
    compteurs = {"refusé": 0, "en cours": 0, "terminé": 0, "relance": 0}
    for page in pages_de_base(token, database_id):
        props = page["properties"]
        nom = titre_page(props)
        statut = nom_select(props.get(DESTAFF_STATUT))
        debut = date_debut(props.get(DESTAFF_DEBUT))
        fin = date_debut(props.get(DESTAFF_FIN))

        # Même règle que pour les besoins : un No-go n'est appliqué qu'avec son motif.
        if statut == "Demande" and nom_select(props.get("Décision")) == "No-go":
            if texte_riche(props.get(DESTAFF_MOTIF_REFUS)):
                ecrire_select(token, page["id"], DESTAFF_STATUT, "Refusé")
                compteurs["refusé"] += 1
                print(f"  → refusé : {nom}")
            else:
                print(f"  · No-go sans motif, laissé en Demande : {nom}")
            continue

        if statut == "Demande validée" and debut and debut <= aujourdhui:
            ecrire_select(token, page["id"], DESTAFF_STATUT, "En cours")
            statut = "En cours"
            compteurs["en cours"] += 1
            print(f"  → en cours : {nom}")

        # Le même passage peut enchaîner les deux transitions, pour une demande
        # validée après sa propre date de fin.
        if statut == "En cours" and fin and fin < aujourdhui:
            ecrire_select(token, page["id"], DESTAFF_STATUT, "Terminé")
            compteurs["terminé"] += 1
            print(f"  → terminé : {nom}")
            continue

        # Le bilan vit dans la base de suivi d'avancement (formulaire « Tracker mon avancement ») : il suffit
        # qu'une entrée soit reliée à la demande.
        if statut != "Terminé" or a_une_relation(props.get(DESTAFF_JOURNAL)):
            continue
        if date_debut(props.get(DESTAFF_RELANCE)) is not None:
            continue
        # « Terminé le » est posé par l'automatisation Notion du passage en Terminé ;
        # à défaut, le lendemain de la date de fin en tient lieu.
        termine_le = date_debut(props.get(DESTAFF_TERMINE_LE))
        if termine_le is None and fin is not None:
            termine_le = date.fromordinal(fin.toordinal() + 1)
        if termine_le is None or (aujourdhui - termine_le).days < RELANCE_BILAN_JOURS:
            continue
        ecrire_date(token, page["id"], DESTAFF_RELANCE, aujourdhui)
        compteurs["relance"] += 1
        print(f"  → relance bilan : {nom}")
    return compteurs


def post_discord(webhook_url, content):
    if DRY_RUN:
        print(f"    [dry-run] posterait sur Discord :\n{content}\n")
        return
    request = urllib.request.Request(
        webhook_url,
        method="POST",
        # allowed_mentions vide : un titre de besoin contenant @ ne doit pinger personne
        data=json.dumps({"content": content, "allowed_mentions": {"parse": []}}).encode(),
        headers={
            "Content-Type": "application/json",
            # NE PAS RETIRER. Cloudflare protège l'API Discord et rejette le User-Agent
            # par défaut de urllib avec un « 403 error code: 1010 ». Il faut un agent
            # explicite. Notion, lui, s'en passe très bien.
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            if response.status not in (200, 204):
                raise RuntimeError(f"Discord a répondu {response.status}")
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"Discord → {error.code} : {detail}") from error


def nom_createur(prop):
    return ((prop or {}).get("created_by") or {}).get("name", "")


def messages_rappel_prevalidation(besoins):
    """Un ou plusieurs messages listant les besoins en attente, chacun sous la limite Discord.

    `besoins` : liste de (nom, catégorie, déposant, âge en jours, url).
    """
    entete = (
        f"⏳ **Besoins en Pré-validation depuis plus de {RAPPEL_PREVALIDATION_JOURS} jours** "
        "— personne n'a encore statué :"
    )
    pied = (
        "👉 Chaque demande doit être **examinée avec son déposant** par le responsable de "
        "sa catégorie (prévenu par e-mail au dépôt), qui renseigne ensuite le champ "
        "**Décision** : `Go` la passe en `Publication` pour lui trouver un owner — ou "
        "directement en `Cadrage métier` si l'**Owner** est déjà renseigné et « Besoin de "
        "contributeurs » à `Non` ; `No-go` la passe en `Rejeté`."
    )
    lignes = []
    for nom, categorie, deposant, age, url in besoins:
        details = " · ".join(
            x for x in (categorie, f"déposé par {deposant}" if deposant else "", f"il y a {age} j") if x
        )
        # Lien masqué et chevrons : sans eux, Discord déplie un aperçu par besoin listé.
        lignes.append(f"• **{nom}** — {details} → [ouvrir](<{url}>)")

    messages, courant = [], [entete]
    for ligne in lignes:
        if len("\n".join(courant + [ligne, pied])) > DISCORD_MAX_CARACTERES:
            messages.append("\n".join(courant))
            courant = [entete + " *(suite)*"]
        courant.append(ligne)
    courant.append(pied)
    messages.append("\n".join(courant))
    return messages


def rappeler_prevalidations(token, database_id, webhook_url, aujourdhui):
    """Poste un rappel groupé pour les besoins coincés en Pré-validation. Retourne leur nombre.

    Le point de départ est la création de la page : le formulaire de dépôt crée tout
    besoin directement en Pré-validation, c'est son état d'entrée. Notion n'expose pas
    la date d'un changement d'état, et poser une date à la première vue (comme pour
    « Date de publication ») retarderait d'autant le rappel des besoins déjà en attente.
    « En pré-validation depuis », si elle est remplie à la main, prime : c'est le moyen
    de recaler le compteur d'un besoin RAMENÉ en Pré-validation depuis un autre état,
    que sa date de création ferait sinon rappeler aussitôt.

    Le rappel se répète tous les RAPPEL_PREVALIDATION_JOURS jours tant que le besoin
    reste en Pré-validation : sortir de cet état est la seule façon de l'arrêter.

    Un seul message pour tous les besoins dus, plutôt qu'un par besoin : au premier
    déploiement, tout l'arriéré arrive d'un coup.
    """
    dus = []
    for page in besoins_dans_etat(token, database_id, "Pré-validation"):
        props = page["properties"]
        depuis = date_debut(props.get(PROP_PREVALIDATION_DEPUIS)) or date.fromisoformat(
            page["created_time"][:10]
        )
        age = (aujourdhui - depuis).days
        if age < RAPPEL_PREVALIDATION_JOURS:
            continue
        if not envoi_du(
            props, PROP_DERNIER_RAPPEL_PREVALIDATION, RAPPEL_PREVALIDATION_JOURS, aujourdhui
        ):
            continue
        dus.append((page, props, age))

    if not dus:
        return 0

    dus.sort(key=lambda d: -d[2])  # les plus anciens d'abord
    besoins = [
        (
            texte_titre(props.get("Nom")) or "(sans titre)",
            nom_select(props.get("Catégorie")),
            nom_createur(props.get("Créé par")),
            age,
            page["url"],
        )
        for page, props, age in dus
    ]
    for message in messages_rappel_prevalidation(besoins):
        post_discord(webhook_url, message)
    # Daté seulement une fois TOUT posté : si Discord échoue en cours de route, le
    # passage suivant reprend l'ensemble — un doublon plutôt qu'un oubli.
    for page, props, age in dus:
        ecrire_date(token, page["id"], PROP_DERNIER_RAPPEL_PREVALIDATION, aujourdhui)
        print(f"  → rappel de pré-validation ({age} j) : {texte_titre(props.get('Nom'))}")
    return len(dus)


def message_annonce(nom, phrase, categorie, url, cherche_contributeurs=True):
    """L'annonce d'un besoin publié.

    Sans recherche de contributeurs, le besoin est quand même annoncé — la visibilité
    est la raison d'être du registre — mais on retire l'appel à candidater, qui serait
    une sollicitation pour rien.
    """
    lignes = [f"📥 **Nouveau besoin interne publié — {nom}**"]
    if phrase:
        lignes.append(f"> {phrase}")
    if categorie:
        lignes.append(f"*Catégorie : {categorie}*")
    if cherche_contributeurs:
        lignes.append(f"Ça t'intéresse ? → {url}")
        lignes.append(PROCEDURE)
    else:
        lignes.append(f"Pour info, ce besoin ne cherche pas de contributeur → {url}")
    return "\n".join(lignes)


def message_relance(nom, phrase, age, url, candidatures):
    """`candidatures` : nombre de candidatures hors brouillon, ou None si inconnu."""
    if candidatures is None:
        etat = f"Publié il y a {age} jours, toujours sans owner."
    elif candidatures == 0:
        etat = f"Publié il y a {age} jours, aucune candidature pour l'instant."
    else:
        etat = (
            f"Publié il y a {age} jours : {candidatures} candidature(s), mais toujours "
            "pas d'owner désigné."
        )
    lignes = [f"⏰ **Toujours personne sur ce besoin — {nom}**", etat]
    if phrase:
        lignes.append(f"> {phrase}")
    lignes.append(f"Un volontaire ? → {url}")
    lignes.append(PROCEDURE)
    return "\n".join(lignes)


def traiter(page, token, webhook_url, aujourdhui, candidatures):
    """Poste au plus un message pour cette page.

    `candidatures` est le nombre de candidatures hors brouillon, ou None si on n'a pas
    pu le calculer. Il ne sert qu'au texte de la relance : ce qui l'arrête, c'est qu'un
    Owner soit renseigné, pas qu'il y ait des candidats.

    Retourne 'annonce', 'relance' ou None.
    """
    props = page["properties"]
    nom = texte_titre(props.get("Nom")) or "(sans titre)"
    url = page["url"]
    phrase = texte_riche(props.get(PROP_PHRASE)) or texte_riche(
        props.get(PROP_PHRASE_AVANT_20260908)
    )
    cherche_contributeurs = nom_select(props.get(PROP_CONTRIBUTEURS)) != "Non"

    # Le compteur de relance a besoin d'un point de départ, et le job en est le seul
    # consommateur : il le pose donc lui-même, au premier passage où le besoin apparaît
    # en Publication sans date (l'automatisation Notion essayée le 2026-08-10 ne
    # remplissait rien). La date est celle du cron, pas de l'instant du changement
    # d'état — sans conséquence pour un seuil à 10 jours.
    publie_le = date_debut(props.get(PROP_PUBLICATION))
    if publie_le is None:
        publie_le = aujourdhui
        ecrire_date(token, page["id"], PROP_PUBLICATION, aujourdhui)
        print(f"  · {nom} : « {PROP_PUBLICATION} » initialisée au {aujourdhui}")

    if not coche(props.get(PROP_ANNONCE)):
        post_discord(
            webhook_url,
            message_annonce(
                nom, phrase, nom_select(props.get("Catégorie")), url, cherche_contributeurs
            ),
        )
        cocher(token, page["id"], PROP_ANNONCE)
        print(f"  → annonce postée : {nom}")
        return "annonce"

    if not cherche_contributeurs:
        return None
    if a_une_relation(props.get(PROP_OWNER)):
        return None

    age = (aujourdhui - publie_le).days
    if age < RELANCE_APRES_JOURS:
        return None
    if not envoi_du(props, PROP_DERNIERE_RELANCE, RELANCE_INTERVALLE_JOURS, aujourdhui):
        return None

    post_discord(webhook_url, message_relance(nom, phrase, age, url, candidatures))
    ecrire_date(token, page["id"], PROP_DERNIERE_RELANCE, aujourdhui)
    print(f"  → relance postée ({age} j sans owner) : {nom}")
    return "relance"


def main():
    token = env("NOTION_TOKEN")
    database_id = env("NOTION_DATABASE_ID")
    webhook_url = env("DISCORD_WEBHOOK_URL")
    candidatures_db = os.environ.get("NOTION_CANDIDATURES_DB_ID")
    webhook_prevalidation = os.environ.get("DISCORD_WEBHOOK_PREVALIDATION_URL")
    aujourdhui = date.today()

    if DRY_RUN:
        print("DRY_RUN actif : rien ne sera posté ni écrit dans Notion.\n")

    if candidatures_db:
        index = index_candidatures(token, candidatures_db)
        print(f"{sum(index.values())} candidature(s) hors brouillon, sur {len(index)} besoin(s)")
    else:
        index = None
        print("! NOTION_CANDIDATURES_DB_ID absent : les relances ne citeront pas le nombre de candidatures.")

    pages = besoins_dans_etat(token, database_id, "Publication")
    print(f"{len(pages)} besoin(s) en État = Publication")

    annonces = relances = 0
    for page in pages:
        nb = None if index is None else index.get(sans_tirets(page["id"]), 0)
        resultat = traiter(page, token, webhook_url, aujourdhui, nb)
        if resultat == "annonce":
            annonces += 1
        elif resultat == "relance":
            relances += 1

    if webhook_prevalidation:
        rappels = rappeler_prevalidations(token, database_id, webhook_prevalidation, aujourdhui)
    else:
        rappels = 0
        print("! DISCORD_WEBHOOK_PREVALIDATION_URL absent : rappels de pré-validation désactivés.")

    print("\nNo-go à appliquer")
    nogos = appliquer_nogos(token, database_id)
    print(f"  {nogos} besoin(s) passé(s) en Rejeté")

    destaff_db = os.environ.get("NOTION_DESTAFF_DB_ID")
    if destaff_db:
        print("\nDemandes de destaff et d'intercontrat")
        c = avancer_destaffs(token, destaff_db, aujourdhui)
        print(f"  {c['refusé']} refusée(s), {c['en cours']} passée(s) en cours, {c['terminé']} terminée(s), {c['relance']} relance(s) de bilan")
    else:
        print("! NOTION_DESTAFF_DB_ID absent : demandes de destaff non traitées.")

    print(f"\nTerminé : {annonces} annonce(s), {relances} relance(s), {rappels} rappel(s) de pré-validation.")


if __name__ == "__main__":
    try:
        main()
    except ConfigError as error:
        print(f"Configuration incomplète : {error}", file=sys.stderr)
        sys.exit(2)
    except Exception as error:  # noqa: BLE001 — on veut un exit code parlant pour Actions
        print(f"Échec : {error}", file=sys.stderr)
        sys.exit(1)
