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

## Comptage des candidatures

La base des besoins n'expose **aucune relation** vers les candidatures : `Besoin` est une
relation à sens unique, portée par la base des candidatures. Aucun rollup ne peut donc
compter les candidats depuis le besoin — un `Nb intéressés` avait été tenté, il renvoyait
`null` en permanence et a été retiré le 2026-08-10. S'y fier aurait fait relancer des
besoins déjà pourvus.

Le job lit donc la base des candidatures et agrège lui-même par besoin. C'est fiable, et
ça permet surtout de **choisir ce qui compte comme candidat** :

| `Statut` | Compte ? | Pourquoi |
|---|---|---|
| `Brouillon` | non | le bouton « Candidater » crée la candidature dans cet état ; une automatisation Notion la bascule en `Intéressé` dès que la `Motivation` est remplie, ce qui fait de ce champ le geste de validation |
| `Décliné` | non | le déposant a refusé ce candidat, donc le besoin cherche toujours quelqu'un — c'est précisément là que la relance sert |
| `Intéressé`, `Retenu` | oui | quelqu'un est sur le coup |

Corollaire à garder en tête : côté vitrine, **le nombre de candidats n'est plus affiché**
aux Busters. Le rétablir demanderait de passer `Besoin` en relation bidirectionnelle, puis
d'ajouter un rollup sur la base des besoins.

## Règles

- **Annonce** : `État = Publication` et `Annoncé sur Discord` décochée.
- **Relance** : `État = Publication`, `Annoncé sur Discord` cochée, `Relancé sur Discord`
  décochée, **aucune candidature qui compte** (cf. tableau ci-dessus), et publié depuis
  10 à 60 jours.
  Au-delà de 60 jours on n'insiste plus : le besoin relève d'un arbitrage de la commission,
  pas d'un rappel automatique.
- Une seule relance par besoin. Si des relances répétées s'avèrent nécessaires à l'usage,
  il suffira de décocher `Relancé sur Discord`.

`Date de publication` est posée **par le job lui-même**, au premier passage où un besoin
apparaît en Publication sans date. C'est le point de départ du compteur de relance.

Une automatisation Notion avait été envisagée pour ça, mais elle ne remplissait rien en
pratique (constaté le 2026-08-10, la date restait vide au passage en Publication comme en
Cadrage métier). Le job étant le seul consommateur de cette date, il est aussi le mieux
placé pour la poser : un mécanisme de moins à maintenir. Contrepartie : la date est celle
du passage du cron, pas de l'instant exact du changement d'état — sans conséquence pour un
seuil à 10 jours.

## La procédure de candidature est dans le message

Le lien posté est celui de **la page du besoin** — c'est l'URL que Notion expose, et
c'est aussi celle qu'on partage à la main sur Discord. Cette page s'ouvre sur une
vingtaine de propriétés : un mode d'emploi placé dans son corps passerait sous la ligne
de flottaison, personne ne le lirait.

Les deux messages rappellent donc la procédure en une phrase (constante `PROCEDURE`) :
cliquer sur **Candidater**, puis écrire sa **Motivation**, faute de quoi la candidature
reste un brouillon invisible. Le même texte figure sur la page d'accueil du registre et
dans la description du champ `Motivation`, pour ceux qui arrivent autrement.

## Configuration

Trois secrets de dépôt (Settings → Secrets and variables → Actions) :

| Secret | Où le trouver |
|---|---|
| `NOTION_TOKEN` | intégration interne Notion, voir ci-dessous |
| `NOTION_DATABASE_ID` | id de « Base des besoins internes » dans son URL |
| `NOTION_CANDIDATURES_DB_ID` | id de « Base de candidatures à un besoin » |
| `DISCORD_WEBHOOK_URL` | Modifier le salon → Intégrations → Webhooks |

`NOTION_CANDIDATURES_DB_ID` est le seul optionnel. S'il manque, le job continue
d'annoncer mais **ne relance plus** : sans savoir qui a candidaté, mieux vaut une relance
manquante qu'une relance sur un besoin déjà pourvu.

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
