#!/usr/bin/env python3
"""Annonce sur Discord les besoins internes publiés, et relance ceux que personne ne prend.

Le job interroge Notion, il n'attend aucun appel entrant. Trois messages :
  - annonce : un besoin est en État = Publication et n'a pas encore été annoncé
  - relance : un besoin publié depuis RELANCE_APRES_JOURS jours n'a aucune candidature
  - rappel de pré-validation : un besoin attend en État = Pré-validation depuis
    RAPPEL_PREVALIDATION_JOURS jours, sans que personne n'ait statué (autre channel)

Toute la mémoire vit dans Notion (cases « Annoncé sur Discord », « Relancé sur
Discord » et « Rappel pré-validation envoyé »), jamais ici. Le job peut donc tourner en double, planter et redémarrer
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

RELANCE_APRES_JOURS = 10  # âge minimum d'un besoin sans candidature pour être relancé
RELANCE_AGE_MAX = 60  # au-delà, on n'insiste plus : c'est à la commission de trancher

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
# (prévenu par e-mail au dépôt) n'a pas statué. Passé ce délai, on le rappelle — une
# seule fois par besoin, pour ne pas transformer le channel en bruit de fond.
RAPPEL_PREVALIDATION_JOURS = 5

# Un message Discord est plafonné à 2000 caractères ; on découpe la liste en dessous.
DISCORD_MAX_CARACTERES = 1900

PROP_ANNONCE = "Annoncé sur Discord"
PROP_RELANCE = "Relancé sur Discord"
PROP_PUBLICATION = "Date de publication"
PROP_RAPPEL_PREVALIDATION = "Rappel pré-validation envoyé"
PROP_PREVALIDATION_DEPUIS = "En pré-validation depuis"

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
        "sa catégorie (prévenu par e-mail au dépôt), afin de passer son **État** en "
        "`Publication` ou en `Rejeté`."
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

    Un seul message pour tous les besoins dus, plutôt qu'un par besoin : au premier
    déploiement, tout l'arriéré arrive d'un coup.
    """
    dus = []
    for page in besoins_dans_etat(token, database_id, "Pré-validation"):
        props = page["properties"]
        if coche(props.get(PROP_RAPPEL_PREVALIDATION)):
            continue
        depuis = date_debut(props.get(PROP_PREVALIDATION_DEPUIS)) or date.fromisoformat(
            page["created_time"][:10]
        )
        age = (aujourdhui - depuis).days
        if age < RAPPEL_PREVALIDATION_JOURS:
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
    # Coché seulement une fois TOUT posté : si Discord échoue en cours de route, le
    # passage suivant reprend l'ensemble — un doublon plutôt qu'un oubli.
    for page, props, age in dus:
        cocher(token, page["id"], PROP_RAPPEL_PREVALIDATION)
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


def message_relance(nom, phrase, age, url):
    lignes = [
        f"⏰ **Toujours personne sur ce besoin — {nom}**",
        f"Publié il y a {age} jours, aucune candidature pour l'instant.",
    ]
    if phrase:
        lignes.append(f"> {phrase}")
    lignes.append(f"Un volontaire ? → {url}")
    lignes.append(PROCEDURE)
    return "\n".join(lignes)


def traiter(page, token, webhook_url, aujourdhui, candidatures):
    """Poste au plus un message pour cette page.

    `candidatures` est le nombre de candidatures hors brouillon, ou None si on n'a pas
    pu le calculer — dans ce cas on n'annonce que, sans jamais relancer : mieux vaut
    une relance manquante qu'une relance sur un besoin déjà pourvu.

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
    if coche(props.get(PROP_RELANCE)):
        return None
    if candidatures is None or candidatures > 0:
        return None

    age = (aujourdhui - publie_le).days
    if age < RELANCE_APRES_JOURS or age > RELANCE_AGE_MAX:
        return None

    post_discord(webhook_url, message_relance(nom, phrase, age, url))
    cocher(token, page["id"], PROP_RELANCE)
    print(f"  → relance postée ({age} j sans candidature) : {nom}")
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
        print("! NOTION_CANDIDATURES_DB_ID absent : relances désactivées (annonces actives).")

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
