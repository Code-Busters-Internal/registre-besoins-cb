# Notifier — Registre des besoins internes CB

Poste sur le channel Discord `#besoins-internes` les besoins internes qui passent en
**Publication**, puis les relance tous les 10 jours tant qu'ils n'ont pas d'**Owner**.
Sur un second channel, il rappelle tous les 5 jours les besoins qui restent en
**Pré-validation**.

Le job **interroge Notion**, il n'expose aucune URL et n'attend aucun appel entrant.
Il est planifié toutes les 2 heures en heures ouvrées via GitHub Actions. GitHub en
saute une large part quand il est chargé : depuis le 2026-08-27, ~2 passages par jour
seulement, à des heures irrégulières, que le cron soit à 2 h, 1 h ou 15 min (constaté le
2026-10-07). Le job étant
idempotent, ça ne fait que retarder un envoi. Pour forcer un passage : Actions →
*Run workflow*, `dry_run` décoché.

## Pourquoi un job planifié plutôt qu'un webhook Notion

Notion sait envoyer un webhook, mais son corps n'est **pas** façonnable : il émet son
format d'API (`{"data": {"properties": {…}}}`) alors que Discord exige une chaîne à la
racine (`{"content": "…"}`). Vérifié empiriquement le 2026-08-10 en pointant une
automatisation Notion sur une URL de test. Brancher Notion sur Discord imposerait donc
un service intermédiaire pour traduire le JSON — un endpoint public de plus à héberger.
Ce job supprime ce besoin : il lit et il poste.

Contrepartie assumée : l'annonce n'est pas instantanée, elle part au prochain passage du
cron (souvent moins d'une heure, mais sans garantie). Pour un registre qui reçoit quelques besoins par mois, c'est sans
conséquence.

## Idempotence

Aucun état n'est stocké ici. Trois propriétés Notion font mémoire :

| Propriété | Rôle |
|---|---|
| `Annoncé sur Discord` | cochée après l'annonce, empêche de la reposter |
| `Dernière relance Discord` | date de la dernière relance, espace les suivantes de 10 jours |
| `Dernier rappel pré-validation` | date du dernier rappel, espace les suivants de 5 jours |

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
- **Relance** : `État = Publication`, `Annoncé sur Discord` cochée, **`Owner` vide**,
  `Besoin de contributeurs` différent de `Non`, publié depuis 10 jours ou plus, et
  dernière relance vieille d'au moins 10 jours. Elle se répète **sans limite de durée** :
  renseigner un Owner (ou sortir le besoin de Publication) est la seule façon de
  l'arrêter. Le nombre de candidatures ne décide plus de rien, il ne sert qu'au texte :
  « aucune candidature », ou « N candidature(s), mais toujours pas d'owner désigné ».

- **Rappel de pré-validation** : `État = Pré-validation`, page créée depuis **5 jours ou
  plus**, et dernier rappel vieux d'au moins 5 jours (jours calendaires ; le cron ne
  tournant qu'en semaine, un délai échu le week-end part le lundi). Tous les besoins dus
  partent dans **un seul message** (découpé s'il dépasse la limite Discord), posté sur le
  channel de `DISCORD_WEBHOOK_PREVALIDATION_URL`. Il rappelle que chaque demande s'examine **avec
  son déposant**, puis que le responsable renseigne le champ `Décision`. Il se répète tant que le
  besoin reste en Pré-validation.

  Le point de départ est la **date de création** de la page, parce que le formulaire crée
  tout besoin directement en Pré-validation et que Notion n'expose pas la date d'un
  changement d'état. La date `En pré-validation depuis`, si on la remplit à la main,
  prime sur la date de création : c'est elle qu'on règle pour un besoin *ramené* en
  Pré-validation depuis un autre état, ou pour tester.

`Date de publication` est posée **par le job lui-même**, au premier passage où un besoin
apparaît en Publication sans date. C'est le point de départ du compteur de relance.

Une automatisation Notion avait été envisagée pour ça, mais elle ne remplissait rien en
pratique (constaté le 2026-08-10, la date restait vide au passage en Publication comme en
Cadrage métier). Le job étant le seul consommateur de cette date, il est aussi le mieux
placé pour la poser : un mécanisme de moins à maintenir. Contrepartie : la date est celle
du passage du cron, pas de l'instant exact du changement d'état — sans conséquence pour un
seuil à 10 jours.

## Sortie de Pré-validation : le champ `Décision`

Le validateur ne change pas l'État à la main : il renseigne `Décision`, et deux
automatisations **Notion** (pas ce job) déplacent le besoin dans la seconde. Elles ne
s'appliquent qu'à un besoin en `Pré-validation`.

| `Décision` | Owner renseigné et `Besoin de contributeurs = Non` ? | Nouvel État |
|---|---|---|
| `Go` | oui | `Cadrage métier` |
| `Go` | non | `Publication` (on y cherche l'owner, relances comprises) |
| `No-go` | — | `Rejeté`, **par ce job**, et seulement si `Motif de rejet` est rempli |

Le No-go est appliqué par le job (`appliquer_nogos`) et non par Notion : les automatisations
Notion n'ont pas de condition « texte non vide », la règle « pas de No-go sans motif »
(2026-10-06) n'y est donc pas exprimable. Le validateur reçoit un rappel Notion tant que le
motif manque ; le passage en `Rejeté` déclenche le mail au déposant.

## Owner et page de suivi (`suivre_owners`, `recopier_declarations_suivi`)

C'est le **validateur** qui choisit l'`Owner` d'un besoin ; l'owner choisit ensuite les
contributeurs. `Owner` est une relation vers l'annuaire, inutilisable comme destinataire
d'une automatisation Notion : le job recopie le compte Notion de l'owner (propriété
`Person` de sa fiche annuaire) dans `Owner (compte)`.

| Condition | Écriture |
|---|---|
| `Owner` renseigné, `Owner (compte)` différent | `Owner (compte)` = compte de l'owner |
| `Owner` renseigné et `État = Publication` | `État = Cadrage métier` (le Go le fait déjà directement si l'owner est choisi avant) |
| Cadrage métier, Cadrage technique ou En cours d'implémentation, `Suivi` vide, dernière demande ≥ 7 j | `Suivi demandé le` = aujourd'hui → mail Notion à l'owner |
| Ligne non recopiée dans « Pages de suivi des besoins » | `Suivi` du besoin = lien déclaré, ligne cochée `Recopié` |

Un owner n'a qu'un accès en lecture à la base des besoins : il déclare son lien avec le
formulaire « Déclarer la page de suivi de mon besoin », et le job le recopie. Cette étape
tourne **avant** les annonces Discord, pour qu'un besoin qui vient de recevoir son owner
quitte Publication sans être annoncé.

## Destaff et intercontrat (`avancer_destaffs`)

Actif seulement si `NOTION_DESTAFF_DB_ID` est défini. Le job ne fait qu'**écrire des
propriétés** sur la base des demandes : les mails partent des automatisations Notion, qu'une
écriture par l'API déclenche bien.

| Situation | Condition | Écriture |
|---|---|---|
| Destaff `Demande`, `Décision = No-go` | `Motif de refus` rempli | `Statut = Refusé` |
| `Demande validée` | début ≤ aujourd'hui | `Statut = En cours` |
| `En cours` | fin < aujourd'hui | `Statut = Terminé` (le lendemain de la date de fin) |
| Intercontrat `En cours` | une tranche de 3 jours depuis le début vient de s'écouler | `Période de suivi` = la tranche → mail « 🔄 Tracke ton intercontrat » |
| `Terminé` | 7 j après `Terminé le`, aucune entrée liée dans `Avancement`, `Relance bilan` vide | `Relance bilan` = aujourd'hui → mail de relance |

`Période de suivi` et `Relance bilan` font aussi office de mémoire d'idempotence. Le job ne
tournant qu'en semaine, seule la dernière tranche écoulée est notifiée.

L'automatisation `Go` calcule l'État par une formule :
`if(and(not(empty(Page.Owner)), Page.Besoin de contributeurs == "Non"), "Cadrage métier", "Publication")`.
Il faut donc renseigner l'Owner et `Besoin de contributeurs` **avant** de mettre `Go`.
Testé le 2026-10-02 sur les quatre combinaisons, État mis à jour en ~10 s.

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

Les secrets de dépôt (Settings → Secrets and variables → Actions) :

| Secret | Où le trouver |
|---|---|
| `NOTION_TOKEN` | intégration interne Notion, voir ci-dessous |
| `NOTION_DATABASE_ID` | id de « Base des besoins internes » dans son URL |
| `NOTION_CANDIDATURES_DB_ID` | id de « Base de candidatures à un besoin » |
| `DISCORD_WEBHOOK_URL` | Modifier le salon → Intégrations → Webhooks |
| `DISCORD_WEBHOOK_PREVALIDATION_URL` | idem, sur le channel des rappels de pré-validation |
| `NOTION_DESTAFF_DB_ID` | id de « Demandes de destaff et d'intercontrat » (optionnel) |
| `NOTION_SUIVI_BESOINS_DB_ID` | id de « Pages de suivi des besoins » (optionnel : sans lui, les liens déclarés ne sont pas recopiés) |

`DISCORD_WEBHOOK_PREVALIDATION_URL` est optionnel : s'il manque, seuls les rappels de
pré-validation sont désactivés.

`NOTION_CANDIDATURES_DB_ID` est optionnel aussi. S'il manque, les relances partent quand
même (c'est l'Owner qui les arrête) mais sans citer le nombre de candidatures.

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
