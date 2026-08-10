# Notifier — Registre des besoins internes CB

Poste sur le channel Discord `#besoins-internes` les besoins internes qui passent en
**Publication**, et relance ceux que personne ne prend au bout de 10 jours.

Le job **interroge Notion**, il n'expose aucune URL et n'attend aucun appel entrant.
Il tourne toutes les 2 h en heures ouvrées via GitHub Actions.

## Pourquoi un job planifié plutôt qu'un webhook Notion

Notion sait envoyer un webhook, mais son corps n'est **pas** façonnable : il émet son
format d'API (`{"data": {"properties": {…}}}`) alors que Discord exige une chaîne à la
racine (`{"content": "…"}`). Vérifié empiriquement le 2026-08-10 en pointant une
automatisation Notion sur une URL de test. Brancher Notion sur Discord imposerait donc
un service intermédiaire pour traduire le JSON — un endpoint public de plus à héberger.
Ce job supprime ce besoin : il lit et il poste.

Contrepartie assumée : l'annonce n'est pas instantanée, elle part au prochain passage du
cron (2 h au pire). Pour un registre qui reçoit quelques besoins par mois, c'est sans
conséquence.

## Idempotence

Aucun état n'est stocké ici. Deux cases à cocher dans Notion font mémoire :

| Propriété | Rôle |
|---|---|
| `Annoncé sur Discord` | cochée après l'annonce, empêche de la reposter |
| `Relancé sur Discord` | cochée après la relance, empêche de relancer en boucle |

Le job peut donc tourner en double, échouer et redémarrer sans jamais poster deux fois.
Et l'état reste lisible à l'œil dans la base, sans consulter de logs.

## Règles

- **Annonce** : `État = Publication` et `Annoncé sur Discord` décochée.
- **Relance** : `État = Publication`, `Annoncé sur Discord` cochée, `Relancé sur Discord`
  décochée, `Nb intéressés = 0`, et publié depuis 10 à 60 jours.
  Au-delà de 60 jours on n'insiste plus : le besoin relève d'un arbitrage de la commission,
  pas d'un rappel automatique.
- Une seule relance par besoin. Si des relances répétées s'avèrent nécessaires à l'usage,
  il suffira de décocher `Relancé sur Discord`.

`Date de publication` est remplie par une automatisation Notion au passage en Publication.
C'est le point de départ du compteur — si elle manque, le job le signale dans ses logs et
ne relance pas.

## Configuration

Trois secrets de dépôt (Settings → Secrets and variables → Actions) :

| Secret | Où le trouver |
|---|---|
| `NOTION_TOKEN` | intégration interne Notion, voir ci-dessous |
| `NOTION_DATABASE_ID` | id de « Base des besoins internes » dans son URL |
| `DISCORD_WEBHOOK_URL` | Modifier le salon → Intégrations → Webhooks |

L'intégration Notion se crée sur <https://www.notion.so/my-integrations> (type *interne*),
puis **la base doit lui être explicitement connectée** : ouvrir « Base des besoins
internes » → menu `⋯` → Connexions → ajouter l'intégration. Sans cette étape, l'API
répond 404 sur une base qui existe pourtant.

## Tester sans rien poster

Onglet Actions → *Notifier les besoins internes* → **Run workflow**. L'entrée `dry_run`
est cochée par défaut : le job affiche les messages qu'il enverrait, sans rien poster sur
Discord ni écrire dans Notion. Décoche-la pour un vrai envoi.

## Lancer en local

```sh
export NOTION_TOKEN=secret_…
export NOTION_DATABASE_ID=…
export DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/…
DRY_RUN=1 python notify.py
```

Python 3.12, aucune dépendance : stdlib uniquement.
