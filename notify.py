#!/usr/bin/env python3
"""Annonce sur Discord les besoins internes publiés, et relance ceux que personne ne prend.

Le job interroge Notion, il n'attend aucun appel entrant. Deux messages :
  - annonce : un besoin est en État = Publication et n'a pas encore été annoncé
  - relance : un besoin publié depuis RELANCE_APRES_JOURS jours n'a aucune candidature

Toute la mémoire vit dans Notion (cases « Annoncé sur Discord » et « Relancé sur
Discord »), jamais ici. Le job peut donc tourner en double, planter et redémarrer
sans jamais poster deux fois la même chose — et l'état reste lisible à l'œil dans
la base.

Variables d'environnement :
  NOTION_TOKEN          token d'une intégration interne Notion, la base doit lui être connectée
  NOTION_DATABASE_ID    id de « Base des besoins internes »
  DISCORD_WEBHOOK_URL   webhook entrant du channel dédié
  DRY_RUN               à 1, affiche ce qui partirait sans rien poster ni écrire
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

RELANCE_APRES_JOURS = 10  # âge minimum d'un besoin sans candidature pour être relancé
RELANCE_AGE_MAX = 60  # au-delà, on n'insiste plus : c'est à la commission de trancher

PROP_ANNONCE = "Annoncé sur Discord"
PROP_RELANCE = "Relancé sur Discord"
PROP_PUBLICATION = "Date de publication"
PROP_CANDIDATURES = "Nb intéressés"

DRY_RUN = os.environ.get("DRY_RUN") == "1"


class ConfigError(RuntimeError):
    pass


def env(name):
    value = os.environ.get(name)
    if not value:
        raise ConfigError(f"variable d'environnement manquante : {name}")
    return value


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


def besoins_publies(token, database_id):
    """Toutes les pages en État = Publication, pagination comprise."""
    pages = []
    cursor = None
    while True:
        payload = {"filter": {"property": "État", "select": {"equals": "Publication"}}}
        if cursor:
            payload["start_cursor"] = cursor
        data = notion_request("POST", f"/databases/{database_id}/query", token, payload)
        pages.extend(data["results"])
        if not data.get("has_more"):
            return pages
        cursor = data["next_cursor"]


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


def nb_candidatures(prop):
    """Le rollup « Nb intéressés ». Tolère un rollup mal typé en retombant sur la relation."""
    if not prop:
        return 0
    if prop.get("type") == "rollup":
        rollup = prop["rollup"]
        if rollup.get("type") == "number":
            return rollup.get("number") or 0
        if rollup.get("type") == "array":
            return len(rollup.get("array", []))
    if prop.get("type") == "relation":
        return len(prop.get("relation", []))
    return 0


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
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            if response.status not in (200, 204):
                raise RuntimeError(f"Discord a répondu {response.status}")
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"Discord → {error.code} : {detail}") from error


def message_annonce(nom, objectif, categorie, url):
    lignes = [f"📥 **Nouveau besoin interne publié — {nom}**"]
    if objectif:
        lignes.append(f"> {objectif}")
    if categorie:
        lignes.append(f"*Catégorie : {categorie}*")
    lignes.append(f"Ça t'intéresse ? Candidate ici → {url}")
    return "\n".join(lignes)


def message_relance(nom, objectif, age, url):
    lignes = [
        f"⏰ **Toujours personne sur ce besoin — {nom}**",
        f"Publié il y a {age} jours, aucune candidature pour l'instant.",
    ]
    if objectif:
        lignes.append(f"> {objectif}")
    lignes.append(f"Un volontaire ? → {url}")
    return "\n".join(lignes)


def traiter(page, token, webhook_url, aujourdhui):
    """Poste au plus un message pour cette page. Retourne 'annonce', 'relance' ou None."""
    props = page["properties"]
    nom = texte_titre(props.get("Nom")) or "(sans titre)"
    url = page["url"]
    objectif = texte_riche(props.get("Objectif"))

    # Le compteur de relance a besoin d'un point de départ. Aucune automatisation Notion
    # ne s'en charge de façon fiable (constaté le 2026-08-10 : la date restait vide au
    # passage en Publication comme en Cadrage métier), donc on la pose ici, au premier
    # passage où le besoin apparaît publié.
    publie_le = date_debut(props.get(PROP_PUBLICATION))
    if publie_le is None:
        publie_le = aujourdhui
        ecrire_date(token, page["id"], PROP_PUBLICATION, aujourdhui)
        print(f"  · {nom} : « {PROP_PUBLICATION} » initialisée au {aujourdhui}")

    if not coche(props.get(PROP_ANNONCE)):
        post_discord(webhook_url, message_annonce(nom, objectif, nom_select(props.get("Catégorie")), url))
        cocher(token, page["id"], PROP_ANNONCE)
        print(f"  → annonce postée : {nom}")
        return "annonce"

    if coche(props.get(PROP_RELANCE)):
        return None
    if nb_candidatures(props.get(PROP_CANDIDATURES)) > 0:
        return None

    age = (aujourdhui - publie_le).days
    if age < RELANCE_APRES_JOURS or age > RELANCE_AGE_MAX:
        return None

    post_discord(webhook_url, message_relance(nom, objectif, age, url))
    cocher(token, page["id"], PROP_RELANCE)
    print(f"  → relance postée ({age} j sans candidature) : {nom}")
    return "relance"


def main():
    token = env("NOTION_TOKEN")
    database_id = env("NOTION_DATABASE_ID")
    webhook_url = env("DISCORD_WEBHOOK_URL")
    aujourdhui = date.today()

    if DRY_RUN:
        print("DRY_RUN actif : rien ne sera posté ni écrit dans Notion.\n")

    pages = besoins_publies(token, database_id)
    print(f"{len(pages)} besoin(s) en État = Publication")

    annonces = relances = 0
    for page in pages:
        resultat = traiter(page, token, webhook_url, aujourdhui)
        if resultat == "annonce":
            annonces += 1
        elif resultat == "relance":
            relances += 1

    print(f"\nTerminé : {annonces} annonce(s), {relances} relance(s).")


if __name__ == "__main__":
    try:
        main()
    except ConfigError as error:
        print(f"Configuration incomplète : {error}", file=sys.stderr)
        sys.exit(2)
    except Exception as error:  # noqa: BLE001 — on veut un exit code parlant pour Actions
        print(f"Échec : {error}", file=sys.stderr)
        sys.exit(1)
