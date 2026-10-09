# Spec — Registre des besoins CB

> **Renommage du 2026-10-08 (retour d'Ophélie, décision Valmon)** : côté Busters, le registre s'appelle **« 🤝 Contribuer à CB »** et un « besoin » s'appelle un **« projet »** : « besoin interne » ne donnait pas envie et ne disait rien de l'impact sur la communauté. Noms actuels : page [Contribuer à CB](https://app.notion.com/p/3b3b91c4eed18151bde4fb6455fdcb24), « Base des projets », « Base de candidatures à un projet », « Pages de suivi des projets » ; colonnes `Titre du projet` (titre), `Le projet en une phrase`, `Projet` (relation, candidatures et pages de suivi), `Proposé par` (ex-`Déposant du besoin`), `Projet lié` (destaff), `Contributeurs (comptes)` (nouveau, rempli par le job pour la vue « 🌟 Mon impact ») ; formulaires « Proposer un projet » et « Déclarer la page de suivi de mon projet » (mêmes liens). La suite de ce document garde « besoin » là où elle décrit l'historique et les décisions passées.

## En une phrase
Un endroit unique où **tous les besoins internes de Code Busters sont cartographiés** — pas seulement des projets : aussi des besoins ponctuels (VT, coaching…) — pour que chacun voie en un coup d'œil ce qui existe, qui le porte, et où ça en est.

> _Élargissement acté lors du call Valmon x Nicolas Girodet (DG) du 2026-08-05 : le registre couvre les **besoins** au sens large, pas que les « projets ». Ex. le besoin de réaliser une VT ou un coaching peut y entrer, avec les bons filtres._

## Le problème
Aujourd'hui les besoins internes CB sont éparpillés à droite à gauche, déliés. Personne n'a de vue d'ensemble : ni les Busters (qui pourraient contribuer), ni les partners (qui pilotent).

## La solution
Une **base unique** (dans Notion) qui liste chaque besoin interne avec ses infos clés, filtrable et tenue à jour. Quand un besoin est publié, une notification prévient les Busters. **Décidé le 2026-08-05** : le *bot* Discord (conversationnel/autonome) est abandonné ; à la place, des **notifications simples segmentées par catégorie de besoin** — vers une mailing liste ou un groupe/channel Discord existant selon le type de besoin (le mapping catégorie → canal reste à faire).

## Ce qu'on décrit pour chaque besoin
- **Nom** — titre du besoin
- **Catégorie** — la **fonction concernée** : Recrutement · RH et culture · Sales · Tech interne · R&D / Innovation · Training · Autre _(`RH` scindé en deux entre le 13/08 et le 08/09, constaté le 2026-09-08)_ _(tranché 2026-08-05 : remplace l'ancienne Catégorie Interne/Externe/R&D, jugée ambiguë par Nicolas Girodet ; `Training` ajouté le 2026-08-13)_
- ~~**Type**~~ — **supprimé le 2026-09-08**, en même temps que les valeurs `Coaching` et `VT`. Il n'avait qu'une seule fonction : piloter le mode de candidature. Coaching et VT sortant du périmètre, il ne reste qu'un mode unique — le champ ne pilotait donc plus rien tout en restant **obligatoire au dépôt**, soit un coût de saisie pur alors que l'adoption est le risque n°1. Un **assessment** reste un besoin du registre : il se qualifie par sa **Catégorie**, comme les autres. _Description d'origine (2026-08-11 → 2026-09-08)_ : la **nature de l'action** : Projet · Coaching · Assessment · VT · Autre _(ajouté le 2026-08-11 après le call Ahmed)_. Axe distinct de la Catégorie, qui dit la **fonction** : un coaching est un besoin `RH` de type `Coaching`. C'est le Type qui pilote le **mode de candidature** (cf. Processus, étape 6) ; la Catégorie pilotera le **canal de notification**. Deux usages différents, donc deux champs — remettre des types d'action dans Catégorie rouvrirait le mélange que Nicolas avait fait fermer le 2026-08-05.
- **Le besoin en une phrase** — à quoi ça sert, en une phrase _(renommé depuis `Objectif` le 2026-09-08)_. ⚠️ **Couplé au code** : `notifier/notify.py` le lit pour la description de l'annonce et de la relance Discord. Le job tournant depuis GitHub Actions, le code déployé et le schéma Notion ne changent jamais au même instant — `notify.py` lit donc **les deux noms** (`PROP_PHRASE` puis `PROP_PHRASE_AVANT_20260908`), ce qui rend la migration insensible à l'ordre. Sans cette tolérance, le renommage aurait produit des annonces **sans description, sans erreur ni log** : `texte_riche(None)` renvoie `""` et `if phrase:` saute simplement la ligne.
- **Détails et valeur ajoutée** — texte long, **obligatoire au dépôt** _(ajouté le 2026-09-08, rendu obligatoire le même jour)_ : le problème, ce que ça change concrètement, ce que ça apporte à CodeBusters. C'est le **pitch au dépôt**, à ne pas confondre avec **`Specs`** (corps de page), qui est le **cadrage détaillé rédigé après le go**. **Pourquoi obligatoire** — il l'était d'abord facultatif, pour ne pas alourdir un dépôt « grosse maille » alors que l'adoption est le risque n°1. La limite Notion sur les droits (ci-dessous) renverse l'arbitrage : si la base passe en lecture seule pour les Busters, **le formulaire est l'unique moment où le déposant peut s'exprimer**, sans seconde chance. Et c'est le seul champ dans ce cas — `Domaine tech`, la date ou la criticité se complètent après coup par la commission ou le tech, alors que le problème et la valeur pour CB sont ce que **personne d'autre que le déposant ne peut écrire**. ⚠️ Le caractère obligatoire est un réglage **du formulaire**, pas de la base : Notion ne connaît pas de propriété obligatoire au niveau du schéma.
- **Besoin de contributeurs** — `Oui` / `Non` _(ajouté le 2026-09-08)_. **À ne pas confondre avec l'état `Publication`** : `Publication` est le go de la commission (le besoin devient visible), `Besoin de contributeurs` dit si on **sollicite des candidatures**. Deux questions distinctes — le champ « Ouvert aux contributions » retiré le 2026-08-05 mélangeait précisément les deux. Un **Select obligatoire** plutôt qu'une case à cocher : une case n'a pas d'état « pas répondu », et décochée par défaut elle rendrait muet tout besoin déposé sans y penser.
- **Périmètre** — ce que ça couvre / ne couvre pas
- **Créé par** — qui a déposé le besoin _(champ système, auto-rempli)_. Un champ **Demandeur** (relation vers l'annuaire) existait pour distinguer le demandeur métier du déposant ; **supprimé le 2026-08-11**, il n'a jamais été rempli autrement qu'en doublon de `Créé par` et faisait courir le risque de notifier la mauvaise personne. À recréer si le cas « déposer pour le compte d'un tiers » se présente vraiment.
- **Owner** — qui porte/dirige le projet une fois lancé
- **Contributeurs** — qui bosse dessus
- **État d'avancement** — Pré-validation · Cadrage métier · Publication · Cadrage technique · En cours d'implémentation · En pause · Livré · **Rejeté** _(`Rejeté` ajouté le 2026-08-13 : le « no-go » de la commission n'avait aucune représentation dans le modèle)_
- **Motif de rejet** — pourquoi le besoin n'est pas retenu (doublon, hors périmètre, pas prioritaire…), rempli par la commission au passage en `Rejeté` _(ajouté 2026-08-13)_. Sert de mémoire : sans motif écrit, la même idée est redéposée à l'identique quelques mois plus tard.
- **Criticité / priorité** — **fixée par le Codir/la commission de validation, jamais par le demandeur** (cf. Processus de validation)
- **Date de delivery** visée
- **Lien vers le suivi** — Kanban/board externe si l'owner en a besoin (optionnel)
- **Domaine tech** — nature du livrable **et** technos concernées, en **choix multiples** : Appli web · Mini-outil · Automatisation · Bot / Assistant · Data / Reporting · Python · Java · C# · Autre. Un besoin peut donc porter `Appli web` + `C#`. _(renommé depuis « Domaine » et passé en multi-select le 2026-08-13, avec les langages absorbés dedans plutôt que dans un champ « Stack » séparé : les deux facettes répondent à la même question, « de quoi ça parle techniquement »)_ Peut être renseigné a posteriori par qui réalise ; laissé **vide** pour un besoin non technique. ⚠️ Ne pas y remettre `Coaching` / `Formation` : ce serait doublonner `Type` et rouvrir le mélange fermé le 2026-08-05 sur `Catégorie`. Pour qualifier un coaching, le bon axe serait la **compétence visée** — champ dédié, à trancher après le pilote d'Ahmed.
- ~~Vocation commerciale~~ / ~~Practice~~ — retirés le 2026-08-05, jugés inutiles
- **Outils impactés** — nouveau champ, liste des outils touchés (ex. Notion + Boon, Popli + intranet…)
- **Specs** — le détail du quoi (pour donner envie et cadrer) — champ le plus important, rempli en dernier lors du cadrage

## Périmètre du registre
- **v1 (validé par les deux partners)** : **exposer / référencer** les projets internes CB + laisser les Busters **se manifester** pour y contribuer. Le choix final de qui participe reste au owner.
- **Inclus** : tous les projets **internes** CB, qu'ils aient une vocation commerciale ou non _(le champ dédié a été retiré le 2026-08-05, jugé inutile — cette distinction n'est plus tracée dans le modèle)_.
- **Hors v1** : le **marché interne / staffing des offres** (pas mûr — le staffing se fait aujourd'hui via bench + Buster Cards + connaissance managers ; la traque technique CB n'est pas encore figée).
- **Hors périmètre — tranché 2026-09-08** : le registre ne gère **ni les VT ni les coachings**. Ils restent dans les process de leurs fonctions (recrutement, mandat d'Ahmed). C'est un **retour** à la ligne v1 validée par les deux partners — le call Ahmed du 2026-08-10 l'avait élargie, et les mécanismes construits les 11 et 13/08 (champ `Type`, assignation directe, `Type de besoin` sur les candidatures) n'existaient que pour le coaching : ils tombent avec lui. Un **second outil relié** pour coaching & formation reste possible plus tard.
- **Reste dans le registre** : les **assessments**, en mode candidature comme un projet.

## Usages visés
- **Voir** : un Buster ouvre le registre et comprend d'un coup d'œil le paysage des projets.
- **Proposer** : quelqu'un avec une idée de projet l'ajoute au registre.
- **Alerter** : à chaque nouveau projet, le bot Discord notifie la communauté (« nouveau projet, venez voir »).
- **Piloter** (v2) : KPI, relances automatiques, alerting sur les projets qui n'avancent pas.

## Processus de validation / cycle de vie du besoin

_Acté lors du call Valmon x Nicolas Girodet (2026-08-05) : rien n'entre dans le registre sans passer par une validation — sinon ça devient n'importe quoi (criticité auto-déclarée, doublons, mini-projets non rationalisés)._

Le champ État porte ces étapes (tranché 2026-08-05) : **Pré-validation → Cadrage métier → Publication → Cadrage technique → En cours d'implémentation → En pause / Livré**, plus **Rejeté** (état terminal, ajouté le 2026-08-13).

1. **Dépôt** — formulaire **simplifié**, grosse maille : présente l'idée / le problème. Objectif : voir s'il y a du jus, avant d'investir du temps de cadrage. État initial : **Pré-validation**. Champs demandés — **état réel constaté le 2026-09-08**, dans l'ordre du formulaire : **Titre du besoin\*** · **Catégorie\*** · **Le besoin en une phrase\*** · Domaine tech · Date estimée de delivery · **Détails et valeur ajoutée\*** · **Besoin de contributeurs\***. _Les deux nouvelles questions sont en fin de formulaire : Notion ajoute toujours une question à la fin et ne la déplace que d'un cran à la fois. Toutes deux ont leur **description affichée** dans le formulaire, pour guider la saisie._

**Avertissement en tête de formulaire** _(ajouté le 2026-09-10)_ — la description du formulaire porte désormais : « ⚠️ Une fois envoyé, un besoin ne peut plus être modifié par son déposant : prenez le temps de remplir « Détails et valeur ajoutée », c'est le seul endroit où vous expliquez le problème et ce que ça apporte à CodeBusters. Pour toute correction, passez par la commission. » Placé **en tête** et non près du bouton Envoyer : un avertissement lu après la saisie n'incite plus à rien. ⚠️ **Il décrit l'état cible, pas l'état actuel** — il ne devient factuellement vrai que le jour où la base A passe en lecture seule, décision encore ouverte (voir « Droits d'édition »). C'est un réglage de **vue**, donc hors de portée de l'API. _`Type` a été ajouté au formulaire en obligatoire le 2026-08-13, puis retiré le 2026-09-08 avec le champ lui-même : sa seule justification était de ne pas laisser un coaching retomber silencieusement en « candidature avec validation »._
2. **Commission de validation** (état **Pré-validation**) — le **binôme Valmon + Nicolas Girodet** examine tous les dépôts en premier (tranché 2026-08-05) ; il décide lui-même, au cas par cas, s'il faut escalader en Codir complet (pas de règle fixe). Il examine le dépôt :
   - **Go / no-go** : est-ce qu'on le publie ou pas (vérifie aussi qu'il n'y a pas déjà un truc existant / une mutualisation possible). Un **no-go** passe l'État à **Rejeté** et remplit **Motif de rejet** ; une automatisation prévient le déposant _(créée le 2026-08-13)_. _Depuis le 2026-10-06, un No-go **sans motif n'est pas appliqué** et l'État ne se change plus à la main en Pré-validation — voir « Sortie de Pré-validation : Décision, motif obligatoire, garde-fou »._
   - **Fixe la criticité / priorité** — jamais le demandeur lui-même, pour éviter que tout le monde marque son besoin "critique".
3. **Cadrage métier** — une fois le go donné, rédaction des **specs détaillées** côté métier (pas forcément avec un tech, selon Nicolas). C'est ce cadrage qui remplit le champ Specs avant publication.
4. **Publication** — le besoin devient visible des Busters : c'est le passage à l'état **Publication** qui déclenche la vue Galerie et la notification (canal à trancher), ce qui remplace le champ "Ouvert aux contributions" retiré le 2026-08-05.
5. **Candidature** — un Buster intéressé clique sur « Candidater », écrit sa **motivation** (c'est elle qui fait passer la candidature de `Brouillon` à `Intéressé` et notifie le déposant).
6. **Examen de la candidature** — fait par le **demandeur** + **un tech** (potentiellement Valmon ou John), pour valider la pertinence technique du candidat.
   - _Jusqu'au 2026-09-08, cette étape n'existait pas pour le coaching (assignation directe). Le coaching étant sorti du périmètre, **l'examen s'applique désormais à tous les besoins** — mode unique._
7. **Cadrage technique** — une fois un contributeur retenu, le tech qui prend le besoin recadre techniquement (le tech doit de toute façon re-comprendre le besoin en profondeur, selon Nicolas).
8. **En cours d'implémentation** → **En pause** / **Livré**.

### ~~Les deux modes de candidature~~ → mode unique — tranché 2026-09-08

> **CADUC depuis le 2026-09-08.** Le double mode n'existait que pour le `Coaching`, sorti du périmètre : **tous les besoins passent désormais par la candidature avec validation**.
>
> ⚠️ **Les automatisations A et B décrites ci-dessous ONT ÉTÉ ÉCRITES**, contrairement à ce que ce document a laissé croire jusqu'au 2026-09-08 (« les deux automatisations à écrire ») et au silence du journal du 13/08. Constaté au navigateur le 2026-09-08 : elles étaient toutes les deux actives sur la base de candidatures. **Supprimer `Type de besoin` en se fiant à la doc aurait coupé la chaîne de notification des candidatures pour TOUS les besoins, en silence** — plus aucun passage en `Intéressé`, plus aucun e-mail au déposant. C'est pour ça que la vérification au navigateur avant suppression est non négociable sur ce projet : l'API n'expose pas les automatisations, donc la seule source de vérité est l'UI, jamais ce fichier.
>
> Traitement effectué le 2026-09-08, dans cet ordre : **1.** retrait du déclencheur `Type de besoin n'est pas Coaching` sur **B**, qui redevient `Motivation modifiée → e-mail + Statut = Intéressé` ; **2.** suppression de **A** ; **3.** retrait de l'action `prop("Type")` du bouton Candidater ; **4.** seulement alors, suppression des propriétés `Type` et `Type de besoin` par l'API. Vérifié après coup : les trois automatisations restantes (celle-ci, `Retenu` → e-mail, `Décliné` → e-mail) sont intactes.
>
> La section est **conservée pour les acquis Notion** qu'elle documente (déclencheurs combinés, formules de bouton, propriétés système vs ordinaires) — ils resservent à chaque automatisation.

_Cadrage d'origine du 2026-08-11 :_ le mode découle du **Type** du besoin, jamais d'un choix du déposant.

| Type | Mode | Statut initial de la candidature | Étape de décision |
|---|---|---|---|
| `Coaching` | **Assignation directe** | `Retenu` | aucune — le déposant est informé, il n'arbitre pas |
| `Assessment`, `Projet`, `VT`, `Autre` | **Candidature** | `Brouillon` → `Intéressé` à la saisie de la motivation | le déposant met `Retenu` ou `Décliné` |

**Pourquoi** : la validation ne se justifie que là où il faut filtrer le candidat — un assessment exige un niveau minimum. Sur du coaching elle ne filtre rien et coûte 4-5 h de latence (Ahmed, 2026-08-10), là où un coup de fil réglait la chose.

**Mécanique — vérifiée dans l'UI Notion le 2026-08-11 (Playwright), l'API n'exposant rien des automatisations.**

Les automatisations acceptent **plusieurs déclencheurs combinés** par « **l'ensemble des conditions** » (ET) ou « l'une des conditions » (OU). Un déclencheur est soit un **événement** (`Ajout de page`, `N'importe quelle propriété modifiée`, `Modification de la propriété X`), soit un **prédicat d'état** sur une propriété, avec les opérateurs **Est · N'est pas · Est modifié · Est effacé** et une sélection de valeurs multiple. On peut donc écrire « quand la Motivation est modifiée **et** que le type est Coaching ».

Limite confirmée au passage : le menu des déclencheurs ne propose que les propriétés **locales** de la base. Le `Type` du besoin est donc bien hors de portée → il est **recopié par le bouton sur la candidature**, comme l'est déjà `Déposant du besoin`. Le champ **`Type de besoin`** (select, mêmes options que `Type`) a été créé sur la base de candidatures le 2026-08-11.

**Les deux automatisations à écrire** (elles remplacent l'actuelle « Motivation modifiée → e-mail + Statut = Intéressé ») :

| | Déclencheurs (l'ensemble des conditions) | Actions |
|---|---|---|
| **A — assignation** | `Modification de la propriété Motivation` **+** `Type de besoin` **Est** `Coaching` | `Statut` = `Retenu` · e-mail au `Déposant du besoin` (« X s'est assigné ») |
| **B — candidature** | `Modification de la propriété Motivation` **+** `Type de besoin` **N'est pas** `Coaching` | `Statut` = `Intéressé` · e-mail au `Déposant du besoin` |

**La recopie passe par une formule, pas par une référence dynamique** (établi le 2026-08-11). Le sélecteur de valeur du bouton n'offre de référence dynamique que pour le titre (texte), `Besoin` (relation) et `Déposant du besoin` (personne) ; pour un **select**, il ne propose que des valeurs statiques — plus l'entrée **« Formule personnalisée »**. C'est elle qui fait le travail : `prop("Type")` dans le bouton « Candidater » remplit `Type de besoin`, **testé OK**.

À retenir sur les formules de bouton, qui corrige une conclusion trop large du 2026-08-05 : l'échec de `prop("Créé par")` tenait à ce que les propriétés **système** (`created_by`) ne sont pas lisibles dans une formule — les propriétés **ordinaires** de la page déclencheuse, elles, le sont parfaitement.

### Pourquoi un bouton + un statut `Brouillon`, et pas un formulaire avec « Envoyer » — 2026-08-13

Question posée par Valmon, tracée ici parce qu'elle reviendra.

**Le bouton est le seul mécanisme qui transporte le contexte du besoin sur la candidature.** Un formulaire Notion n'a aucun contexte : rien ne lui dit sur quel besoin on candidate. Le candidat devrait choisir le bon besoin dans une liste, et surtout **deux** valeurs resteraient vides _(trois avant la suppression de `Type de besoin` le 2026-09-08)_ :
- **`Déposant du besoin`** — la route de notification. Une automatisation ne peut pas traverser une relation pour retrouver le déposant : la valeur doit être **sur la ligne de candidature** (c'est le trou documenté le 06/08 — toute candidature créée hors du bouton envoie un e-mail sans destinataire).
- ~~**`Type de besoin`**~~ — _supprimé le 2026-09-08 (mode unique). Argument d'origine : les déclencheurs d'automatisation ne voient que les propriétés **locales** ; sans recopie, impossible de distinguer assignation directe et candidature validée._ **Conséquence : le bouton n'a plus que deux valeurs à transporter, ce qui rend la piste des liens préremplis nettement plus atteignable.**
- la relation **`Besoin`** elle-même, préremplie sans risque d'erreur.

**Et `Brouillon` existe parce qu'un bouton crée la page immédiatement**, sans boîte de saisie ni événement « envoyer ». Il y a donc forcément une ligne en base entre le clic et la saisie de la motivation — c'était le bug du 06/08 (notification sur « Ajout de page », motivation encore vide). `Brouillon` + déclencheur « Motivation modifiée » **fabrique l'événement de soumission qui n'existe pas**, et le notifier exclut les brouillons de son comptage.

**Piste qui supprimerait les deux, à tester** : *si* Notion accepte des **liens de formulaire préremplis** (paramètres d'URL), une **formule sur la ligne du besoin** peut fabriquer le lien de candidature propre à ce besoin (besoin + déposant + type dedans), et le bouton « Candidater » ne serait plus qu'un lien vers un vrai formulaire avec « Envoyer ». On gagnerait au passage la disparition de la page à 20 propriétés qui a obligé à expliquer la procédure à trois endroits. **Non vérifié** — c'est tout l'enjeu du test.

**Conséquences sur le notifier** (`notifier/notify.py`), non traitées :
- ~~la phrase de procédure postée sur Discord dit « clique sur **Candidater** » — fausse pour un besoin auto-assignable~~ → **réglé sans code le 2026-09-08** : sans assignation directe, la phrase (`notify.py:52`) est vraie pour 100 % des besoins ;
- ~~`RELANCE_APRES_JOURS` figé à 10 pour tout le monde, alors qu'Ahmed et Valmon veulent une **cadence par type**~~ → **sans objet le 2026-09-08** : la justification était « quelques heures pour une VT urgente », et les VT sortent du périmètre. La cadence unique de 10 j convient aux projets. _Vérifié le 2026-09-08 : `Type` n'est référencé nulle part dans `notifier/` (seuls hits = en-têtes HTTP `Content-Type`), la suppression du champ est sans effet sur le job._

### Droits d'édition — la limite Notion, posée le 2026-09-08

**Notion n'a pas de permissions par ligne.** Les lignes d'une base héritent des droits de la base, sans exception : « seul le déposant peut modifier son besoin » **n'est pas exprimable nativement**. Soit tout le monde édite toute la base, soit personne.

Pris au pied de la lettre, le besoin exprimé casserait d'ailleurs le processus : c'est la **commission** qui fixe `Criticité / priorité`, fait bouger l'`État` et remplit `Motif de rejet`, et l'**owner / le tech** qui remplit `Domaine tech` et les `Specs` au cadrage. L'intention retenue est donc : *un Buster ne doit pas pouvoir modifier le besoin d'un autre*, déposant et commission gardant la main.

Ce qu'un Buster ordinaire a réellement besoin de pouvoir faire :

| Action | Droit nécessaire sur la base A (besoins) |
|---|---|
| Déposer un besoin | **aucun** — le formulaire Notion fonctionne sans droit d'édition |
| Voir les besoins publiés | lecture |
| Candidater | à vérifier : le bouton crée une ligne dans la **base B**, reste à confirmer qu'il s'utilise depuis une page en lecture seule |

**Conséquences actées : le champ `Détails et valeur ajoutée` passe obligatoire au dépôt (2026-09-08), et un avertissement en tête de formulaire prévient que le dépôt ne sera plus modifiable (2026-09-10)** — en lecture seule, le formulaire est le seul moment où le déposant peut s'exprimer.

Piste complémentaire : le niveau **« Peut commenter »** de Notion donne aux Busters la lecture *et* un canal pour demander une correction sur leur propre besoin, sans ouvrir l'édition. C'est l'entre-deux le plus proche de l'intention, à défaut de droits par ligne.

D'où la piste : **base A en lecture pour tous, édition réservée à la commission**. Contrepartie assumée — le déposant ne peut alors plus modifier son propre besoin non plus ; Notion n'offre pas d'entre-deux. L'alternative est l'édition ouverte à tous, avec `Créé par` pour l'attribution, l'historique de page pour revenir en arrière, et une convention écrite — le compromis habituel, mais purement social.

⏳ **Rien à faire tant que l'espace est privé** (il l'est toujours). Le sujet devient réel au moment du partage.


### Routage des notifications de dépôt par catégorie — 2026-09-10

Au **dépôt** d'un besoin, le responsable de la fonction concernée est prévenu par e-mail. Sept automatisations sur la base A, toutes déclenchées par `Page added` **et** `Catégorie is set to X` :

| Catégorie | Destinataires (À) | CC |
|---|---|---|
| Recrutement | Quitterie Hubault · Jonathan Jayet · Ophélie | Valmon Leymarie |
| RH et culture | Ophélie | Valmon Leymarie |
| Tech interne | Jonathan Jayet · Valmon Leymarie | — |
| R&D / Innovation | Jonathan Jayet | Valmon Leymarie |
| Sales | Nicolas GIRODET · Aly-Bocar Cisse · Matthieu BARRAL | Valmon Leymarie |
| Training | Ahmed Dammak | Valmon Leymarie |
| Autre | Ophélie · Nicolas GIRODET · Valmon Leymarie | — |

_2026-10-06 (décision Valmon)_ : Valmon est **en copie** de toutes les catégories où il ne décide pas, pour suivre chaque demande et voir si elle avance. En CC et non en À : le mail s'adresse aux validateurs, Valmon n'a pas de pouvoir de décision sur ces pôles.

**Ce que ça ne referme pas.** À ne pas confondre avec le trou tracé depuis le 2026-08-05 (« mapper chaque catégorie vers son canal »), qui porte sur la notification **à la communauté au passage en `Publication`** — Discord aujourd'hui, mailing listes pour certaines catégories. **Celui-là reste ouvert.** Ici on notifie des **individus au dépôt**, pas la communauté à la publication : deux moments et deux audiences distincts.

**Déclenchement au dépôt, donc avant le go/no-go.** Choix assumé : le responsable de la fonction est souvent le mieux placé pour peser sur la décision de la commission. Contrepartie — ces personnes sont prévenues de besoins qui finiront parfois `Rejeté`. Si ça devient bruyant, le déclencheur à basculer est `État = Publication` au lieu de `Page added`.

**Ce que dit le mail — corrigé le 2026-09-17.** La première rédaction annonçait « la commission (Valmon + Nicolas) va l'examiner. Tu es prévenu en tant que responsable du sujet ». Faux sur le fond : elle mettait le destinataire en position de spectateur consulté, alors que **c'est lui qui instruit**. Texte en vigueur : le besoin est en `Pré-validation`, **c'est au(x) destinataire(s) de l'examiner**, en se synchronisant entre eux et **avec le déposant du besoin**, puis de statuer. Deux variantes selon le nombre de destinataires — « synchronisez-vous entre vous et avec le déposant » à plusieurs, « prends contact avec le déposant » pour `RH et culture`, `R&D / Innovation` et `Training` où il n'y a qu'une personne. `Autre` garde en plus sa consigne de vérifier que le besoin ne relevait pas d'une catégorie existante, une ligne mal catégorisée n'atteignant pas le bon responsable.

**Lien vers le besoin — ajouté le 2026-10-01.** Jusque-là les 7 messages étaient en texte brut, sans aucune mention : les destinataires ne savaient pas de quel besoin il s'agissait. Chaque message se termine désormais par « Voir le besoin : » + la mention **Page de déclenchement** (menu `@` → *Lien vers la page*). L'**objet** porte aussi le nom du besoin et le déposant : `Nouveau besoin interne déposé — <Catégorie> : <Nom> (déposé par <Créé par>)`. ⚠️ À la relecture d'un message, vérifier la présence des **mentions** (puces grises), pas seulement le texte.

**Mail refondu le 2026-10-06** (Valmon trouvait le paragraphe unique illisible). Texte brut imposé par l'action « Envoyer un e-mail » de Notion (pas de gras, pas de bouton, mention « Envoyé via Notion Automations » non retirable), mais les retours à la ligne et les emojis passent dans Gmail — vérifié par un dépôt de test. Objet : `📥 Besoin à valider · <Catégorie> · <Nom> (déposé par <Créé par>)`. Corps : bonjour → « <Créé par> vient de déposer un besoin interne : <Nom> » → « 👉 Ouvrir le besoin : <lien> » → « Vous recevez ce mail car vous validez la catégorie « X » » → bloc « ✅ CE QU'ON ATTEND DE VOUS » (1. lire et discuter avec le déposant ; 2. remplir « Décision » en haut de la fiche, avec les trois cas Go / Go + Owner + « Besoin de contributeurs » = Non / No-go + Motif de rejet) → « ℹ️ l'état change tout seul » → « ⏰ rappel Discord tous les 5 jours ». `Autre` garde un encadré « ⚠️ vérifiez la catégorie » avant le bloc ✅. La variante à un seul destinataire a disparu : « (et entre vous) » figure aussi dans les mails à une personne, **gardé tel quel par décision de Valmon**. ⚠️ Pour insérer le lien vers le besoin, le bouton `@` du champ ne propose que les **propriétés** de la page ; il faut taper `@` au clavier puis « Page de décl » et choisir l'entrée sous *Lien vers la page*.

**Un dépôt envoie deux e-mails** : l'alerte au(x) responsable(s) de la catégorie, et le mail de l'automatisation `Page added` préexistante (« X a créé une demande de besoin interne »). ⚠️ _Corrigé le 2026-10-01_ : ce second mail a été décrit jusqu'ici comme une « confirmation au déposant », c'est faux — son destinataire est **fixé sur Valmon** (vérifié dans l'UI), quel que soit le déposant ; le déposant ne reçoit rien. Conséquence : sur `Tech interne` et `Autre`, où Valmon est aussi destinataire du routage, **il reçoit deux mails pour chaque dépôt**, quel qu'en soit l'auteur. **Gardé tel quel par décision de Valmon (2026-10-01)** : c'est la copie admin de tous les dépôts, réservée à l'équipe qui porte le registre — les responsables de catégorie (Jon, Ophélie…) n'y sont pas et ne reçoivent donc qu'un mail. **Alexandre Lemonnier ajouté** comme destinataire le 2026-10-01 : il reprend le chantier pendant le congé paternité de Valmon (il a déjà l'accès complet à la base). **2026-10-06 : Valmon retiré de cette copie admin, Alexandre seul destinataire** pendant le congé (décision Valmon) — Valmon suit désormais via le CC des sept mails de routage, ce qui supprime son doublon.

**Pourquoi sept automatisations et pas une.** Notion ne sait pas résoudre dynamiquement des destinataires : le champ « À » n'accepte que des personnes choisies ou des adresses saisies, jamais une formule. Une propriété `people` « Personnes à notifier » alimentée automatiquement aurait demandé… sept automatisations pour la remplir. Coût de maintenance assumé : changer un responsable = éditer l'automatisation concernée.

⚠️ **Piège de l'UI, rencontré deux fois** : dans le sélecteur de valeurs d'une condition, **toutes les options sont cochées par défaut**. Cliquer une valeur la **retire** au lieu de la sélectionner — on obtient « toutes sauf X ». La manœuvre correcte est : cliquer `Any option` pour tout décocher, **vérifier que le compte est à zéro**, puis cocher la seule valeur voulue.

⚠️ **Le champ « À » trompe** : une adresse saisie devient une puce distincte du champ de saisie, qui se vide. Le champ paraît vide alors que le destinataire est bien enregistré. Et `Enable` reste grisé tant que **l'objet** n'est pas rempli — ce n'est pas le destinataire qui bloque.

### Sortie de Pré-validation : Décision, motif obligatoire, garde-fou — 2026-10-06

**Déclencheur** : Ophélie avait sorti un besoin de Pré-validation en le mettant **En pause** avec un commentaire, sans Go ni No-go — rien ne l'en empêchait. Une option « À retravailler » a été envisagée puis **écartée par Valmon** : les Busters sont en lecture seule, ils ne pourraient pas retravailler leur besoin. Le validateur n'a donc que **Go / No-go** (option « Retour au déposant » supprimée), et un besoin à retravailler est un **No-go motivé** que le déposant redépose.

| Mécanisme | Où | Comportement |
|---|---|---|
| `Décision = Go` | automatisation Notion (inchangée) | État → `Publication` ou `Cadrage métier` selon Owner / Besoin de contributeurs |
| `Décision = No-go` | automatisation « Décision No-go → rappel motif obligatoire (validateur) » | mail à celui qui a mis le No-go : « Ton No-go sera appliqué seulement quand le Motif de rejet est rempli. Assure-toi qu'il le soit. » (texte de Valmon) |
| No-go **+ motif rempli** | **job `notifier/`** (`appliquer_nogos`) | État → `Rejeté`, au passage horaire suivant |
| `État = Rejeté` | automatisation « Rejeté → motif au déposant (redépôt possible) » | mail au déposant avec le motif et l'invitation à redéposer un besoin retravaillé |
| État changé à la main en Pré-validation | automatisation « Garde-fou : pas de changement d'État sans Décision » | si l'État passe dans l'un des 8 autres états alors que `Décision` n'est ni Go ni No-go → État remis en `Pré-validation` + mail à l'auteur du changement (~5-10 s) |

**Pourquoi le job et pas Notion pour le No-go** : les automatisations Notion n'ont **pas de condition « texte vide / non vide »** — sur une propriété texte, laisser la valeur vide transforme la condition en « Modification de la propriété ». La règle « motif rempli » n'est donc exprimable que dans le job.

`Motif de rejet`, `Décision` et `État` sont **épinglés en tête** de la fiche du besoin. Les automatisations « À retravailler » et l'ancienne « No-go → Rejeté » directe ont été supprimées.

⚠️ **Coalescence des événements** (rencontré en test) : Notion ne déclenche rien si une valeur est effacée puis remise en quelques secondes — il ne voit pas de changement net. Espacer les modifications de ~45 s pour tester.


### Owner, Cadrage métier et page de suivi — 2026-10-07

**Rôles (décision Valmon)** : c'est le **validateur** qui fait avancer l'État — lui seul en a le droit — et qui **choisit l'owner** ; l'**owner choisit les contributeurs**.

| Règle | Mécanisme |
|---|---|
| Go avec un Owner déjà choisi → **Cadrage métier** ; Go sans owner → Publication | automatisation « Décision Go → Cadrage métier (si owner) ou Publication », formule `if(not(empty(Page.Owner)), "Cadrage métier", "Publication")` — avant le 2026-10-07 il fallait aussi « Besoin de contributeurs » = Non |
| Owner renseigné sur un besoin en Publication → **Cadrage métier** (même s'il cherche encore des contributeurs) | job (`suivre_owners`), avant les annonces Discord |
| `Owner (compte)` = compte Notion de l'owner | job : `Owner` est une relation vers l'annuaire, inutilisable comme destinataire ; le job lit `Person` dans la fiche annuaire |
| En Cadrage métier / Cadrage technique / En cours d'implémentation, `Suivi` vide → mail « 🗂️ Ta page de suivi » à l'owner, relance tous les 7 jours | job pose `Suivi demandé le` → automatisation « Owner choisi → demande de page de suivi (owner) » |
| L'owner déclare le lien → `Suivi` du besoin | formulaire « Déclarer la page de suivi de mon besoin » (base **Pages de suivi des besoins**, `8ecc3c43…`) → job (`recopier_declarations_suivi`) recopie et coche `Recopié` |

**Pourquoi un formulaire** : un owner est un Buster, en lecture seule sur la base des besoins ; il ne peut pas coller lui-même le lien dans `Suivi`. Lien du formulaire : `https://app.notion.com/p/13da20440dc748ca9396c5b7dba20d20`. La base est en lecture pour tous, accès complet Valmon, Alexandre, Nico, groupe Partner.

**Au déploiement** (décision Valmon) : seul « Enregistrement de réunion » (Cadrage métier) a reçu la demande ; « Podcast busters » (Accepté) et « Compte-rendu de validation technique » (En pause) sont hors des états concernés.

**Pas encore fait** : le circuit des candidatures (mail « nouvelle candidature », décision Retenu / Décliné) passe toujours par le **déposant** ; Valmon a décidé qu'il passe à l'**owner**. Point à régler : pendant la Publication il n'y a pas encore d'owner, les premières candidatures servent justement au validateur à le choisir.

## Destaff et intercontrat — 2026-10-06

**Origine** : retour d'Ophélie sur le « journal d'intercontrat » — l'onboarding des nouveaux en sort (il est relié à ce qui existe déjà côté People), on y ajoute le **destaffing**, et c'est le **manager** qui suit. Le lien depuis le Playbook manager est **reporté** jusqu'à validation par Ophélie.

**Emplacement** : page [📒 Destaff et intercontrat](https://app.notion.com/p/3f1b91c4eed18195bdc4d940c64a7b39), **à côté de Besoins internes** sous « Registre des besoins CB (privé — brouillon) ». Périmètre : **tout CB**. On déplacera les deux pages ensemble une fois validées.

### Deux bases

| Base | Rôle | Saisie |
|---|---|---|
| **Demandes de destaff et d'intercontrat** (`66466dce…`) | une ligne = **une période** (destaff ou intercontrat) | formulaire « 📝 Faire une demande » |
| **Suivi d'avancement (destaff et intercontrat)** (`2c53099a…`) | une ligne = une entrée de suivi, reliée à sa demande (`Demande` ↔ `Avancement`) | formulaire « 📝 Tracker mon avancement », ou bouton **« Tracker l'avancement »** sur la demande (comme « Candidater » côté besoins) |

**Deux bases gardées (décision Valmon)** : une demande reçoit plusieurs entrées de suivi, notamment une tous les 3 jours en intercontrat. Le suivi est inline sur la page sous « Suivi d'avancement ».

**Demande — champs** : Intitulé de ta demande\* · Situation\* (Destaff / Intercontrat) · Partner responsable\* (Valmon, Jon, Aly ou Ahmed) · Manager\* · Date de début\* · Date de fin _(facultative ; texte : « Obligatoire pour un destaff ; facultative pour un intercontrat si tu ne la connais pas encore »)_ · Nombre de jours\* · Rythme\* · Type d'activité\* · Objectif\* · Besoin interne lié _(seul champ facultatif hors date de fin)_. Champs gérés : `Buster` (created_by), `Statut`, `Décision`, `Motif de refus`, `Terminé le`, `Relance bilan`, `Période de suivi`. La colonne « Besoin d'aide » a été retirée. **Épinglés en tête de fiche** : Décision, Statut, Partner responsable, Motif de refus. Dans les vues table, le bouton **« Tracker l'avancement » suit directement l'intitulé**. **Suivi d'avancement : propriété « Besoin interne lié »** (rollup automatique via `Demande` → `Besoin interne lié`, affiché sur chaque fiche de suivi, pas dans les vues) — ajoutée le 2026-10-07.

**Base « 📊 Bilan destaff par Buster » (2026-10-08)**, sous la page « Destaff et intercontrat » : **une ligne par Buster** (une vue groupée de la base des demandes affichait une ligne par demande, ce que Valmon ne voulait pas — Notion ne sait pas agréger les lignes d'une vue). Colonnes : `Buster` (titre), `Grade` (rollup de `Fiche Buster` → annuaire), `Jours destaff` et `Jours IC` (sommes des formules du même nom sur ses demandes), `Quota destaff (j)` (formule selon le grade), `Destaff consommé` (formule texte stylée : jours ÷ quota en %, **vert jusqu'à 100 %, rouge au-delà** ; « pas de quota » pour un Bronze). Côté demandes : `Fiche Buster` et `Synthèse Buster` (relation double sens avec `Demandes`), toutes deux posées par le job (`relier_fiches_buster`), qui crée la ligne du Buster au besoin ; `Jours destaff` = destaff validé, en cours ou terminé débutant dans l'année civile, `Jours IC` = intercontrat débutant dans l'année. **Quota** tiré du modèle de rémunération 2026 (page « Rémunération & Avantages chez CB 2026 ») : jours de mission pris en compte Silver 216 / Gold 214 / Diamond 210 sur une base de 218 j travaillés (~252 ouvrés − ~35 congés et RTT) → **2 / 4 / 8 jours** de destaff, ce qui recoupe la colonne « Jours de destaff » du même tableau. **Bronze : pas de quota défini.**

**Entrée de suivi — champs** : Demande\* · Ce que j'ai fait\* · Livrables / liens · Du\* · Au\*. Le titre `En une ligne` n'est plus demandé (2026-10-06) : l'automatisation « Titre auto des entrées de suivi » le pose à la création, « Suivi du <Du> au <Au> ». `Type d'activité` n'y figure pas : il est déjà sur la demande.

### Cycle de vie

- **Destaff** : `Demande` → `Demande validée` → `En cours` → `Terminé` (ou `Refusé`). Le **partner responsable** décide via `Décision` (Go / No-go), le manager en copie.
- **Intercontrat** : `En cours` → `Terminé`, pas de validation. Sans date de fin, c'est le partner responsable qui le passe en `Terminé`.

### Notifications et transitions

| Événement | Mécanisme | Destinataires |
|---|---|---|
| Destaff déposé → `Statut = Demande` | automatisation | **À** partner responsable · **CC** manager |
| Intercontrat déclaré → `Statut = En cours` | automatisation | — |
| `Décision = Go` → Statut **selon les dates** : `Terminé` si la fin est passée (et `Terminé le` = aujourd'hui), `En cours` si le début est passé, sinon `Demande validée` | automatisation (formule, 2026-10-07) | **À** Buster · **CC** Nico, manager, partner |
| `Décision = No-go` sans motif | automatisation : rappel « motif obligatoire » | celui qui a mis le No-go |
| No-go **+ Motif de refus rempli** → `Refusé` | **job** | — |
| `Statut = Refusé` | automatisation : motif + lien pour redéposer | **À** Buster · **CC** Nico, manager, partner |
| `Demande validée` et début ≤ aujourd'hui → `En cours` | **job** | — |
| `En cours` et fin < aujourd'hui → `Terminé` (donc **le lendemain** de la date de fin) | **job** | — |
| `Statut = Terminé` → pose `Terminé le` + mail « 📝 Tracke ton avancement » | automatisation | **À** Buster · **CC** manager |
| Terminé depuis 7 j sans entrée de suivi → pose `Relance bilan` → mail de relance | **job** + automatisation | **À** Buster · **CC** manager, partner |
| Intercontrat en cours : tous les 3 jours → pose `Période de suivi` → mail « 🔄 Tracke ton intercontrat · <du → au> » | **job** + automatisation | **À** Buster seul |
| `Statut` changé à la main alors que `Décision` est vide (destaff) | garde-fou : Statut remis à `Demande` + mail | auteur du changement |

**Demande validée après coup (2026-10-07)** : une demande dont les dates sont déjà passées au moment du Go passe **directement** en `Terminé`, sans attendre le job (Clément, demande du 6 validée le 7 : restée en `Demande validée` parce que le job GitHub n'avait pas tourné). Une modification faite par une automatisation Notion **ne déclenche pas** les autres automatisations (testé : le passage en `Terminé` par le Go n'a pas lancé « Terminé → tracker ») : l'automatisation Go pose donc elle-même `Terminé le`, et c'est **le mail de Go** qui porte la demande de tracking (il contient déjà le lien du formulaire ; phrase « Ta demande avance seule selon ses dates… (dès maintenant si elle est déjà passée) »). Le mail « 📝 Tracke ton avancement » ne part pas dans ce cas ; la relance J+7 du job reste en place.

**Mails de suivi** (les trois derniers mails « tracke ») : ils portent **uniquement le lien vers le formulaire « Tracker mon avancement »**, pas de lien vers la demande (décision Valmon 2026-10-06). Ce lien est le **lien de partage du formulaire** (`https://app.notion.com/p/f8fc06fb5d504b2eae01be346f2eee42`), pas l'URL de la vue `?v=…` : avec des droits d'édition sur la base, l'URL de vue ouvre l'**éditeur** du formulaire (même piège que le formulaire de dépôt en août). Un formulaire Notion ne se préremplit pas : le Buster choisit sa demande dans la liste, le mail lui en rappelle l'intitulé.

**Ton des mails au Buster** (décision Valmon 2026-10-06) : aucune mention du type « ton manager et le partner sont en copie » ni de menace de relance — jugé passif-agressif. La relance J+7 dit « Si ce n'est pas encore fait, prends 5 minutes… Merci ! » ; le mail de fin de période « Une entrée suffit, et ça prend 5 minutes ». Les copies restent, seuls les mails adressés au partner les mentionnent.

**Tranches de 3 jours** (`derniere_tranche` dans `notify.py`) : découpées depuis la date de début (1→3, 4→6…), bornées par la date de fin. Le job écrit la dernière tranche **entièrement écoulée** si elle diffère de `Période de suivi`, ce qui déclenche le mail. Le job ne tournant qu'en semaine, une tranche finie le week-end part le lundi ; si plusieurs tranches se sont écoulées entre deux passages, seule la dernière est notifiée.

**Pourquoi le job pose des dates plutôt qu'envoyer lui-même** : Notion envoie les mails (depuis le compte de Valmon, avec les mentions), le job ne fait qu'écrire une propriété — une écriture par l'API **déclenche bien** les automatisations Notion. `Relance bilan` et `Période de suivi` servent à la fois de déclencheur et de mémoire d'idempotence.

### Droits

Notion (offre actuelle) n'a **ni règles par ligne ni droits par propriété**, et une base partagée en édition laisse un Buster créer une ligne sans passer par le formulaire. La **page** elle-même est en lecture seule pour les membres, accès complet Valmon + Alexandre (corrigé le 2026-10-07 : elle était en accès complet pour tous). Réglage retenu sur les deux bases : **lecture seule pour les membres** (base dissociée du parent pour couper le partage hérité), les formulaires restant soumettables. Accès complet : Valmon, Alexandre, Nico et le groupe Partner (2026-10-07 ; avant : Jon, Aly, Ahmed en « modifications de contenu »). Les **pages d'accueil** (Besoins internes, Destaff et intercontrat) ne sont modifiables que par Valmon, Alexandre et Ophélie. À vérifier avec un Buster en lecture seule (Clément) : pas de bouton « Nouveau », le bouton « Tracker l'avancement » et les formulaires fonctionnent.

## Choix techniques (pistes, à confirmer)
- **Source de vérité** : Notion, idéalement branché à l'annuaire.
- **Notifs** : bot Discord (voir sous-projet `../discord_bot`).
- **Tickets / suivi** : Linear évoqué comme option.
- Débat ouvert : RAG dédié vs lecture directe Notion — non tranché.

## Modèle de données (Notion)

_Implémenté le 2026-08-05 dans un espace **privé** (non partagé) : [Registre des besoins CB (privé — brouillon)](https://app.notion.com/p/3b3b91c4eed18191b49edda343d4f23c), avec [Besoins internes](https://app.notion.com/p/8ce5614800ca437899ea76f99f4ebc1e) et [Candidatures / Intérêts](https://app.notion.com/p/d612839a23934b078146fe818951b356). Relation bidirectionnelle entre les deux bases (rollup "Nb intéressés" fonctionnel). Demandeur/Owner/Contributeurs/Personne pointent vers `BDD Annuaire Busters` en relation à **sens unique**, pour ne pas modifier le schéma de la base annuaire partagée tant que c'est un brouillon privé — à revoir en two-way au moment du partage si utile._

_Page front-door créée le 2026-08-05 : **[Besoins internes](https://app.notion.com/p/3b3b91c4eed18151bde4fb6455fdcb24)** — une seule page avec le formulaire « Déposer un besoin » en en-tête et la table complète en dessous (au lieu de deux onglets séparés). La base brute reste accessible pour l'édition admin ; son ancien onglet formulaire a été fermé._

_**Introduction ajoutée en tête de cette page le 2026-08-13**, écrite en partant du problème. Constat en 5 points : les Busters ne s'investissent pas · aucune visibilité ni format commun · canal de communication pas clair · initiatives mal référencées et compliquées à suivre · aucune visibilité sur les réalisations. Puis la réponse en trois temps : (a) l'endroit unique où un besoin est déposé, arbitré, publié, suivi ; (b) **« tout besoin qui mobilise un Buster passe par ici »** — projet, cadrage, assessment, présentation, training, quelle qu'en soit la taille, la règle étant que ce qu'un Buster prépare seul reste chez lui. _Réécrit le 2026-09-08_ : `VT` et `coaching` retirés de l'énumération, et **la contrepartie ajoutée explicitement** — « Deux exceptions : les VT et les coachings, qui ne passent pas par ici — ils restent gérés par leurs process existants ». Une porte d'entrée doit dire ce qui n'entre pas, sinon les gens déposent quand même ; (c) **« ça ne remplace pas vos process, ça les référence »** — le registre se branche sur les pages et bases Notion existantes, ce qu'on centralise c'est le référencement et la visibilité, pas la façon dont chaque fonction travaille. _Réécrit le 2026-09-08_ : les exemples « un plan de coaching, un suivi de VT » remplacés par « le board d'une fonction, une base métier, un suivi en place » — ils étaient devenus trompeurs, laissant croire que le registre référence les coachings alors qu'il ne les touche plus du tout ; (d) **« ce qui est tracé ici compte »** — lien direct avec la page des réalisations et l'estimation des primes communautaires. Les points (c) et (d) sont les deux réponses écrites au risque d'adoption soulevé par Ahmed : (c) désarme l'objection « chaque fonction a déjà son board », (d) donne l'incitation qui manquait._

### Base A — `Besoins internes` (base pivot, anciennement « Projets internes »)
Une ligne = un besoin (projet, VT, coaching…). La **page** du besoin porte les specs détaillées (rich text).

| Propriété | Type | Détail / valeurs |
|---|---|---|
| **Nom** | Title | Titre du besoin |
| **Catégorie** | Select | **Recrutement · RH et culture** · Sales · Tech interne · R&D / Innovation · Training · Autre _(⚠️ `RH` a été scindé en `Recrutement` + `RH et culture` entre le 2026-08-13 et le 2026-09-08 — changement **constaté** dans la base le 2026-09-08, ni l'auteur ni la raison ne sont tracés)_ _(fonction concernée — tranché 2026-08-05, remplace l'ancienne valeur Interne/Externe/R&D demandée par Aly, jugée ambiguë par Nicolas Girodet ; `Training` ajouté le 2026-08-13)_ |
| **Le besoin en une phrase** | Text | À quoi ça sert, en une phrase — _renommé depuis `Objectif` le 2026-09-08_. ⚠️ **lu par `notify.py`** (description de l'annonce et de la relance) |
| **Détails et valeur ajoutée** | Text | **Obligatoire au dépôt** — le pitch : le problème, ce que ça change, ce que ça apporte à CB _(ajouté 2026-09-08)_. Obligatoire parce qu'en base lecture seule le déposant n'a pas de seconde chance, et que lui seul peut l'écrire |
| **Besoin de contributeurs** | Select | `Oui` · `Non` — sollicite-t-on des candidatures ? _(ajouté 2026-09-08)_. `Non` → annonce Discord sans appel à candidater et **aucune relance**. **Vide = traité comme `Oui`** (fail-safe : les besoins déjà en base ne deviennent pas muets) |
| ~~**Périmètre**~~ | — | ⚠️ **N'existe pas dans la base** (constaté le 2026-09-08 : 20 propriétés réelles, pas de `Périmètre`). Soit jamais créé, soit supprimé sans trace. À recréer si le besoin est réel |
| **Créé par** | Created by _(système)_ | Qui a déposé le besoin — seule identité du déposant depuis la suppression de `Demandeur` le 2026-08-11 |
| **Owner** | Relation → `BDD Annuaire Busters` (max 1) | Qui le porte une fois lancé |
| **Contributeurs** | Relation → `BDD Annuaire Busters` | Qui bosse dessus |
| **État** | Select _(et non Status, malgré ce qui était écrit ici — constaté le 2026-08-13)_ | Pré-validation · Cadrage métier · Publication · Cadrage technique · En cours d'implémentation · En pause · Livré · **Rejeté** _(tranché 2026-08-05 ; `Rejeté` ajouté le 2026-08-13, et l'ordre des options remis dans l'ordre du processus au passage — ⚠️ **cet ordre n'a pas tenu** : constaté le 2026-09-08, `Publication` est repassé avant `Cadrage métier`)_ |
| **Motif de rejet** | Text | Pourquoi le besoin n'est pas retenu, rempli par la commission au passage en `Rejeté` _(ajouté 2026-08-13)_ |
| **Criticité / priorité** | Select | Basse · Moyenne · Haute · Critique — **fixée par la commission de validation (Codir), jamais par le demandeur** _(Nicolas Girodet)_ |
| **Date de delivery** | Date | Cible |
| **Domaine tech** | Multi-select | Appli web · Mini-outil · Automatisation · Bot / Assistant · Data / Reporting · Python · Java · C# · Autre _(renommé depuis « Domaine » et passé en multi-select le 2026-08-13 : absorbe la stack, plusieurs valeurs possibles ; peut être rempli a posteriori par qui réalise, laissé vide pour un besoin non technique)_ |
| **Outils impactés** | Multi-select | Ex. Notion, Boon, Popli, intranet… _(nouveau — Nicolas Girodet, pour repérer les outils qui reviennent souvent et rationaliser)_ |
| **Suivi** | URL | Lien vers le suivi du besoin, **renseigné par l'owner** : une page Notion à part ouverte à tout CB, un kanban, un Trello… Chaque contributeur y note où il en est, pour que les suivants reprennent — _délégué (Aly) ; rendu explicite le 2026-10-07, et rappelé aux Busters dont le destaff / l'intercontrat est lié au besoin (formulaire et mails de suivi)_ |
| ~~**Nb intéressés**~~ | ~~Rollup~~ | **Retiré le 2026-08-10** : il renvoyait `null` en permanence (relation à sens unique portée par la base des candidatures). Le job `notifier/` agrège lui-même — la table le listait encore à tort jusqu'au 2026-09-08 |
| **Specs** | Corps de page | Le détail, en rich text, rédigé lors du cadrage (après le go de la commission) |

### Base B — `Candidatures / Intérêts` (volet « mobiliser »)
Une ligne = un Buster qui se manifeste sur un projet. Remplie via un **formulaire Notion** (comme le form « Crée ton profil » de l'annuaire).

| Propriété | Type | Détail / valeurs |
|---|---|---|
| **Candidature** | Title | Préremplie par le bouton avec le nom du besoin |
| **Créé par** | Created by _(système)_ | Le candidat. Remplace `Personne` (relation vers l'annuaire), supprimée le 2026-08-05 : le bouton ne pouvait pas la remplir, elle serait restée vide |
| **Besoin** | Relation → `Besoins internes` | Le besoin visé — **renommée depuis `Projet` le 2026-08-11**, le registre couvre des besoins et plus seulement des projets |
| **Statut** | Select | Brouillon · Intéressé · Retenu · Décliné _(décision au déposant, sans justif — Aly)_ |
| **Motivation** | Text | Message libre du candidat — sa saisie vaut validation de la candidature |
| **Déposant du besoin** | People | Recopié par le bouton : route de notification, une automatisation ne peut pas traverser une relation |
| **Date** | Created time | Auto |

> _Examen de la candidature (Nicolas Girodet) : fait par le **demandeur** + **un tech** (potentiellement Valmon ou John), pour valider la pertinence technique avant décision du owner._

### Vues prévues (base A)
- **Galerie** filtrée sur État = **Publication** = le **portail** pour les Busters (exposer) — remplace le champ « Ouvert aux contributions » retiré le 2026-08-05.
- **Board par État** (pilotage).
- **Table** complète + filtres par Catégorie / Criticité.

### Ce que le modèle ne fait PAS (hors v1)
- Le **marché interne / staffing des offres** (Aly : pas mûr).
- Le **bot conversationnel / RAG** → sous-projet `../discord_bot`. Ici, seule l'**alerte native « nouveau projet »** (webhook Notion → Discord) est dans le périmètre.

## Discussion — retours des partners

_Points remontés lors des échanges de cadrage. Non tranchés : servent à faire mûrir la spec._

### Avec John — `meeting/2026-07-10_projet_interne_cb_x_JOnh.txt`
- **Champs de la fiche projet** validés ensemble : nom, objectif, périmètre, owner, contributeurs (a minima à l'instant T), état d'avancement (en cours / en pause / personne dessus), date de delivery, criticité / priorisation, specs.
- **Périmètre** : a minima les projets **internes**, à vocation commerciale ou non (le noter comme attribut). Coaching / formation : bonne idée d'essayer de le caler dedans, sinon second outil séparé.
- **Idée forte** : un demandeur (partner ou Buster) ajoute son idée de projet → un **agent/bot Discord** annonce le nouveau projet à la communauté.
- **Source de vérité** : Notion, branché à l'annuaire.
- **Débat technique — RAG vs Notion** : Notion n'est pas vectorisé ; piste d'un RAG synchronisé (idée attribuée à Kevin). Mais si le bot doit aussi **écrire** dans Notion (pas que lire), le RAG ne répond qu'à la lecture → un RAG n'est peut-être pas justifié pour de la simple consultation. **Non tranché.**
- **Coût** : passer par l'**API Claude** (compte CB non-nominatif à créer) plutôt que self-host GPU. Self-host = plutôt un sujet 2027. Ordres de grandeur discutés (≈ Sonnet 5, réductible avec Haiku ; routeur de modèles selon le type de requête). ⚠️ Risque de « premature optimization ».
- **Tickets** : Linear évoqué comme option (a un MCP).

### Avec Aly — `meeting/2026-07-10_Aly_x_Projet_carto_interne.txt`
- **« Deux projets en un »** — distinction clé :
  - (a) **Exposer / référencer** les initiatives internes + laisser les gens se manifester → **OK, utilisable tout de suite**, aucun problème.
  - (b) **Marché interne / staffing des offres** → **beaucoup plus compliqué, pas mûr**. Aujourd'hui le staffing se fait « à la baïonnette » (dispo/bench, sinon reco ou sortie de mission) et s'appuie sur les Buster Cards + la connaissance managers ; la traque technique CB n'est pas encore figée. **À sortir du périmètre v1.**
- **Triptyque du besoin** : **exposer → mobiliser → suivre.** Les Busters se portent volontaires ; le choix final du staffing reste au owner, sans justification à fournir.
- **Nouvel attribut demandé** : **`catégorie`** (interne / externe / R&D…).
- **Suivi délégué au owner** : chaque projet embarque un système de suivi (ticketing / roadmap / backlog / board agile) **choisi par son owner**, mais présent dans l'outil.
- **Points communautaires** : saisir les actions au moment où on les prévoit + cocher « fait » + générer du **reporting** → arrêter de courir après les gens. L'outil pourrait résoudre ça.
- ⚠️ **Costing** : un outil imposé coûte cher à monitorer / maintenir / modifier en prod → **à intégrer au chiffrage** dès le départ.

### Avec Nicolas Girodet (DG) — `../../recording/2026-08-05_spec_pour_le_registre_des_besoins_CB.txt`
- **Élargissement du périmètre** : le registre couvre les **besoins**, pas que les projets (ex. VT, coaching). Nom du besoin, pas nom du projet.
- **Processus de validation en 2 temps** (nouveau, cf. section dédiée) : dépôt simplifié → commission (Codir / Valmon+Nicolas) go/no-go + criticité → cadrage → publication → candidature → examen par demandeur + tech.
- **Qui priorise** : la commission/le Codir, jamais le demandeur — sinon tout le monde marque son besoin "critique".
- **Cartographie des process métiers CB** (idée de Nicolas) : dessiner les workflows de chaque fonction (recrutement, sales…) pour repérer où l'IA peut aider, y compris pour des besoins remontés par des non-tech (ex. Camille) qui n'auraient pas idée que l'IA peut résoudre leur problème. **Jugé comme un projet de second temps** par Valmon : vient après que l'outil de dépôt existe, pas en v1.
- **Champs** : nouveau **Domaine** (appli web, mini-outil…, rempli a posteriori par qui réalise) + nouveau **Outils impactés** (liste, ex. Notion + Boon) pour repérer les outils qui reviennent souvent et éviter la prolifération de mini-outils quand on pourrait rationaliser (ex. arrêter Boon).
- **Catégorie — tranché 2026-08-05** : Nicolas pointait que "Catégorie" (interne/externe/R&D) mélangeait la nature du besoin et la fonction concernée. Décision : **Catégorie devient la fonction concernée** (RH, Sales, Tech interne, R&D…), l'ancienne segmentation interne/externe/R&D est abandonnée.
- **Bot Discord remis en cause** : Valmon pense l'abandonner (mail ou autre canal à la place) — **contredit la décision du 2026-07-10** (« webhook Notion → Discord natif »). Mécanisme de notification à retrancher.
- **Nicolas (DG) — pain points** : peu en tant que DG pur, plus côté Sales/Respo Sales. Doit envoyer une liste d'idées par mail (pas encore reçue).
- **Besoins temporels / multi-étapes** — Valmon avait flag que la fiche gère mal ce cas. **Tranché 2026-08-05 : reporté à v2.** En v1, le champ État reste un statut global ; pas de sous-étapes structurées tant qu'on n'a pas de vrais cas d'usage en main.
- _Idées personnelles de Valmon évoquées en marge (hors périmètre du registre, pour mémoire)_ : outil de recording généralisé pour les 1:1 de toute l'équipe (question ouverte sur le stockage des fichiers audio bruts) ; existent déjà comme sous-projets Transfo_AI séparés : tracking coaching, tracking IC.

### Avec Ahmed (mandat onboarding / coaching / assessment) — `meeting/2026-08-10_Ahmed_x_registre_des_besoins.txt`

_Premier call de confrontation du socle v1 à un usage métier réel. Valmon fait la démo complète, Ahmed teste les cas limites._

- ⚠️ **Le précédent qui a échoué** — c'est le point le plus important du call. Nico avait monté un système de ticketing quasi identique pour l'onboarding il y a ~18 mois, au démarrage de Notion : création d'une page → mail + message au validateur. **Ça n'a pas pris, non pas pour une raison technique mais parce que les gens n'étaient pas engagés dans l'outil.** Le risque n°1 du registre n'est donc pas sa mécanique — elle marche déjà — mais son adoption.
- **Chaque fonction a déjà son board.** Sales a « Home Sales » (Nicolas) : clients, missions, VT, base des Busters, entretiens ; il existe aussi une base de déclaration des actions pour les primes, remplie à la main. Ahmed est justement en train de refaire sa partie suivi et se voit rajouter des contraintes d'intégration tous les jours. Faire du registre la **table parent** obligerait à tout rebrancher.
- **Granularité hétérogène** (objection d'Ahmed) : une ligne « assessment de 30 min » à côté d'une ligne « créer la plateforme CB » (3 jours+). Réponse de Valmon : c'est le champ **Charge estimée (jours)**, exactement comme des user stories qui vont de 0,5 à 15 jours.
- **Découpage — la règle est l'atomicité, et c'est le déposant qui tranche** : si des personnes différentes peuvent prendre chaque morceau → une ligne par morceau (cas d'Ahmed : ~30 lignes pour un parcours d'onboarding, 4 assessments + 6 coachings unitaires) ; s'il faut une équipe qui tient le sujet de A à Z pour la consistance → une seule ligne + un lien `Suivi` vers le board (cas d'Aly sur la plateforme DevOps, 30-40 actions mais 3-4 contributeurs fixes).
- **Ce qui reste chez Ahmed vs ce qui vient au registre** — clarification utile : la **préparation** (le Buster bosse seul : fiches, questions, ressources) reste entièrement chez Ahmed. Seul ce qui **mobilise un tiers** (assessment, coaching) s'interface avec le registre.
- **Deux catégories demandées** : `Assessment` et `Coaching`, parce qu'elles n'ont pas le même mode de candidature (cf. Processus, étape 6). → ⚠️ **Caduc au 2026-09-08** : le coaching sort du périmètre, seul l'`Assessment` reste — et sans champ `Type`, il se qualifie par sa Catégorie.
- **Use case pilote acté** : plan de coaching → quand une étape de préparation passe à `Done`, ça crée une action **assessment** → qui crée un besoin dans le registre → notification Discord. → ⚠️ **À rejouer au 2026-09-08** : le pilote portait sur coaching **et** assessment ; seul l'assessment subsiste, donc le pilote se réduit à la branche assessment. C'est lui qui devait trancher *golden copy vs lecture multi-bases* — **le seul arbitrage structurant encore ouvert**. À reconfirmer avec Ahmed, qui avait cadré son parcours d'onboarding sur ~30 lignes dont 6 coachings unitaires désormais hors registre. La base à lire côté Ahmed est **`Action du plan`** (pas `Plan de coaching`), qu'il doit d'abord alléger.
- **Ce que Valmon doit obtenir d'Ahmed pour brancher** : qui notifier (le manager du Buster ? Ahmed ? les deux ?), qui valide une candidature, la catégorie (coaching / assessment), la charge estimée. Point technique : dans `Action du plan`, la `Date` est la **date de réalisation**, pas une échéance — il n'y a donc **aucune due date exploitable** pour l'alerting, alors que c'est précisément sur elle que repose le mécanisme de relance envisagé.
- **Accès manquant** : Valmon n'a pas les droits sur l'espace **Home Sales** → à demander à Nicolas.

**🔴 Le débat non tranché, formulé par Ahmed en fin de call** — *est-ce que l'agent lit une base unique chez Valmon, ou parcourt les bases de chaque fonction ?*
- **Position Ahmed** : chacun crée dans sa propre base, le registre vient **lire** pour faire le ticketing. Les réalisations se reconstituent par vues filtrées sur les bases sources.
- **Position Valmon** : un agent qui dépend de N systèmes casse dès que l'un d'eux bouge — **pas scalable**. Et il veut *un seul endroit* recensant tout ce sur quoi les Busters se sont investis, parce que c'est ce qui permet d'attribuer la **prime communautaire** en fin d'année (et d'expliquer l'intercontrat).
- **Compromis proposé par Ahmed** : la **golden copy** — chaque action réalisée dans la base d'une fonction est recopiée dans le registre, avec ou sans notification. Chacun garde sa base, le registre garde sa vue unique.
- **Conclusion** : on ne tranche pas dans l'abstrait, on teste sur le pilote coaching/assessment d'Ahmed.

---
_Essence issue des CR de cadrage dans `meeting/` et du `journal.md`. Créé le 2026-07-10, mis à jour le 2026-08-05 (call Nicolas Girodet), le 2026-08-11 (call Ahmed du 2026-08-10) puis le 2026-08-13 (prépa Codir : Training, Type au formulaire, Domaine tech, Rejeté + Motif de rejet, introduction de la page) et le **2026-09-08 (sortie des VT et des coachings du périmètre : suppression du champ `Type` et du mode « assignation directe » ; refonte du formulaire de dépôt : `Objectif` → `Le besoin en une phrase`, ajout de `Détails et valeur ajoutée` et de `Besoin de contributeurs` ; limite Notion sur les droits par ligne ; mise à jour de la spec sur l'état réel constaté dans Notion)**._
