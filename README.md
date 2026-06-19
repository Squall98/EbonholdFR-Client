# EbonholdFR — Client (traduction française)

Rend le client **Project Ebonhold** (World of Warcraft 3.3.5a, rogue-lite) **entièrement en français** : sorts, talents, echoes, factions, compétences, hauts faits, titres… y compris le contenu custom du serveur.

> ℹ️ Complémentaire de l'addon **EbonholdFR** (qui traduit les descriptions d'echoes via les info-bulles). Ici on traduit le **client lui-même**, au niveau des fichiers de données.

---

## Pourquoi c'est nécessaire

Ebonhold est conçu pour le client **anglais (enUS)**. Si on installe un client **français (frFR)**, le jeu de base passe bien en français, **mais tout le contenu custom du serveur reste vide** : le serveur n'a rempli que la colonne anglaise de ses fichiers de données (`.dbc`), et le client français lit la colonne française… vide.

Ce projet **injecte des traductions françaises dans la colonne française des `.dbc`**, par ordre de priorité :

1. **nos traductions** (`data/custom_translations.json`) — contenu custom : sorts, echoes…
2. sinon le **texte français de base de Blizzard** — sorts/objets standard ;
3. sinon l'**anglais recopié** — pour ne jamais laisser de texte vide.

Résultat : un client Ebonhold quasi 100% en français.

---

## 🟢 Méthode simple (recommandée) — l'installeur

Pour les joueurs : **pas besoin de Python ni de ligne de commande.**

1. Télécharge **`EbonholdFR-Installer.exe`** (dans les *Releases* GitHub).
2. Double-clique dessus.
3. Choisis ton dossier Ebonhold (celui qui contient `Wow.exe`) — il est souvent détecté tout seul.
4. Clique sur **« Mettre Ebonhold en français »**. C'est tout.

Le bouton **« Restaurer l'anglais »** annule tout (une sauvegarde `.bak` est faite automatiquement).

> Pour un jeu **100% français**, installe d'abord le pack de langue **frFR** (gros téléchargement à part). Sans lui, seul le contenu custom du serveur est traduit (le reste du jeu de base reste en anglais). L'installeur te prévient si le pack manque.
> https://drive.google.com/file/d/1j3OuTz1KMUsuUWXQiMJaE0yQXmAobRxu/view

*(Maintenance : l'exe se régénère avec `installer/build_exe.bat` — voir plus bas.)*

---

## Méthode manuelle (scripts) — pour développeurs

### Prérequis

- Une **copie française** de ton client Ebonhold (locale `frFR` installée), **séparée** de ton install d'origine (qui reste intacte comme filet de sécurité).
- **Python 3** avec **mpyq** : `pip install mpyq`
- Le client doit être **fermé** pendant la reconstruction (sinon les fichiers sont verrouillés).

Ce dépôt ne fournit **aucun fichier de jeu** : tu utilises ta propre installation.

---

## Installation

```bash
git clone <ce-depot>
cd EbonholdFR-Client
pip install mpyq
cp config.example.py config.py      # puis édite config.py
```

Dans **`config.py`**, renseigne :

- `SRC_DATA` → dossier `Data` de ton client **original** (anglais, tenu à jour par le launcher) ;
- `DST_DATA` → dossier `Data` de ta **copie française**.

---

## Utilisation

```bash
cd tools
python extract_base_dbc.py     # extrait les Spell.dbc de référence (dans build/)
python rebuild_all.py          # injecte le français et réécrit les patchs FR
```

Lance le jeu depuis ta copie française : c'est en français. 🇫🇷

---

## Mettre à jour après un patch du serveur

1. Laisse le launcher mettre à jour ton client original (`SRC_DATA`).
2. **Ferme le jeu**, puis :

```bash
cd tools
python extract_base_dbc.py
python rebuild_all.py                 # ré-applique toutes les traductions existantes
python extract_custom_spells.py       # liste les NOUVEAUX textes à traduire (s'il y en a)
python auto_translate.py              # traduit automatiquement montures/tomes/motifs simples
```

3. S'il reste des entrées dans la liste, ajoute-les à `data/custom_translations.json`
   (clé = texte **anglais** → valeur = traduction **française**), puis relance `rebuild_all.py`.

---

## Ajouter ou corriger une traduction

Tout vit dans **`data/custom_translations.json`** :

```json
{
  "names": { },
  "descs": {
    "Dash a short distance forward.": "Bondit sur une courte distance vers l'avant."
  }
}
```

- Clé = texte anglais **exact** (avec les codes `$s1`, `$d`, `${...}` tels quels) ;
- Valeur = traduction française (les codes `$...` calculent les chiffres en jeu, à **préserver**).

Puis : `python rebuild_all.py`.

---

## Structure

```
EbonholdFR-Client/
├── installer/                # outil grand public
│   ├── ebonhold_fr_installer.py   # interface graphique (choix dossier + 1 bouton)
│   └── build_exe.bat              # compile l'exe autonome (PyInstaller)
├── config.example.py         # modèle de config (→ config.py, ignoré par git)
├── data/
│   └── custom_translations.json   # LE fichier central des traductions (EN → FR)
├── tools/
│   ├── rebuild_all.py        # script principal : reconstruit le client FR
│   ├── extract_base_dbc.py   # extrait les Spell.dbc de référence
│   ├── extract_custom_spells.py  # liste ce qui reste à traduire
│   ├── auto_translate.py     # traduit montures/tomes/motifs par règles
│   ├── dbc_localize.py       # moteur de fusion .dbc (détection colonnes + merge)
│   └── mpqwrite.py           # créateur d'archive MPQ en Python pur
├── build/                    # artefacts générés (ignoré par git)
├── LICENSE
└── CHANGELOG.md
```

---

## Détails techniques

- **Format `.dbc`** : WotLK 3.3.5a (WDBC). Colonnes localisées détectées automatiquement ; le français s'écrit dans le slot `frFR` (index +2 du bloc localisé).
- **Encodage** : **UTF-8** (le client Ebonhold attend de l'UTF-8 — pas du cp1252).
- **MPQ** : `mpqwrite.py` crée des archives MPQ v1 (secteurs compressés zlib) lisibles par le client 3.3.5a, sans dépendance externe (ni StormLib ni MPQ Editor).
- **Patchs traités** : `patch-5.MPQ` (Spell.dbc + DBC de sorts) et `patch-6.MPQ` (Faction, SkillLine, Achievement, CharTitles…). Une sauvegarde `.bak` est créée à la première écriture.

---

## Limites

Restent en anglais (impossible à corriger côté client) :

- **noms d'objets, de quêtes et de PNJ custom** : envoyés dynamiquement par le serveur (cache `WDB`), pas stockés dans un `.dbc` ;
- **noms** des sorts/echoes custom : volontairement laissés en anglais (cohérence avec les guides et la communauté) ; seules les **descriptions** sont traduites.

---

## Crédits & avertissement

Réalisé par **Squall98**. Projet communautaire **non officiel**, sans affiliation avec Blizzard Entertainment ni Project Ebonhold. Aucun fichier de jeu n'est redistribué. Sous licence MIT (voir `LICENSE`).

