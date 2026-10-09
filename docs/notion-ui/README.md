# Éditer Notion par l'interface (Playwright)

Certaines choses ne passent ni par l'API Notion ni par le MCP :
- le texte des formulaires ;
- les automatisations et leurs mails ;
- les partages.

Ces scripts les font dans l'interface, via le serveur MCP Playwright. On les lance avec
`browser_run_code_unsafe`, dans un navigateur déjà connecté à Notion et ouvert sur la
bonne base.

Les `__PLACEHOLDERS__` se remplacent par du JSON avant le lancement, par exemple avec
`sed` ou un petit script Python, dans une copie du fichier.

## Les scripts

| Script | Ce qu'il fait | Paramètres |
|---|---|---|
| `retext.js` | Remplace des textes du formulaire ouvert : titres et descriptions de questions, description du formulaire | `__REPS__` : `[{old, new}]` |
| `addq.js` | Ajoute des questions à un formulaire | `__QS__` |
| `listauto.js` | Liste les automatisations de la base ouverte | — |
| `dumpauto.js` | Ouvre des automatisations par leur nom et renvoie leurs textes : objet et corps des mails | `__NAMES__` |
| `scanall.js` | Parcourt toutes les automatisations de la base et relève leurs textes | — |
| `candidx.js` | Ouvre une automatisation à partir d'un bout de sa description | `__KEYS__`, `__MODE__` |
| `swap3.js` | Remplace des mots dans les mails d'automatisation. C'est la méthode fiable (voir plus bas). L'exemple fourni remplace « besoin » par « projet ». | `__NAMES__`, à adapter : `LITERALS` et la regex |
| `newauto.js` | Crée une automatisation : nom et déclencheurs | `__NAME__`, `__TRIG__` |
| `recip.js` | Ajoute une action « Envoyer un e-mail » et ses destinataires | `__TO__`, `__CC__`, `__FIRST__` |
| `mailtpl.js` | Remplit l'objet et le corps d'un mail, avec les variables de la page de déclenchement | `__SUBJ__`, `__BODY__`, `__ANCHOR__` |
| `share.js` | Règle les partages de pages | `__OPS__` |

## Pièges connus

**Texte des formulaires**
- Cliquer dans le champ, puis `Meta+A`, puis taper le nouveau texte, puis cliquer en dehors.
- `Escape` annule la modification.
- Une sélection posée par script sans vrai clic n'est pas enregistrée.

**Titre d'un formulaire**
- Renommer la question du titre renomme la colonne titre de la base elle-même.
- Le code doit donc lire la colonne titre par son type, pas par son nom (`titre_de` dans `notify.py`).

**Mails d'automatisation**
- L'éditeur ignore une sélection posée par script tant qu'on n'a pas cliqué pour de vrai sur un caractère visible du même champ. Sans ce clic, le texte tapé atterrit à la fin du champ.
- Il faut aussi que le défilement soit instantané (`behavior: 'instant'`) et suivi d'une attente, avant de calculer les coordonnées du clic.
- Il faut éviter les puces de mention (`contenteditable=false`) et la barre d'outils @/Σ qui recouvre le bas du champ.
- `swap3.js` applique tout ça et vérifie `getSelection()` avant de taper.
- Après chaque modification, relancer `dumpauto.js` pour vérifier le résultat.

**Panneau des automatisations**
- Il s'ouvre avec le bouton dont l'`aria-label` contient « Automatisations ».
- Pour ouvrir une automatisation : taper son nom dans le champ de recherche, puis cliquer la première carte, environ 118 px sous le champ.

**Changements de schéma**
- Passer par l'API REST : `PATCH /v1/databases/{id}`, Notion-Version 2022-06-28.
- Ne pas passer par `notion-update-data-source` du MCP : ses ADD/DROP COLUMN ont supprimé des formulaires, dont les liens de partage étaient alors à refaire partout.
