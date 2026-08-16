# MAJ du patch FR — manuel pour l'IA locale

Ce document contient **tout ce qu'il faut** pour mettre à jour le patch de traduction
française d'Ebonhold après une mise à jour du serveur, **en local**, sans dépendre d'une
IA cloud. Il est écrit pour être lu aussi bien par Dylan que par une IA locale
(qwen3-coder) qui pilote le travail.

---

## 1. Le cerveau (matériel + modèles)

- **Machine** : RTX 5090 Laptop **24 Go VRAM**, 64 Go RAM, Core Ultra 9 275HX.
- **Modèle de code / agent** : **`qwen3-coder:30b`** (Ollama) — le meilleur codeur qui
  tient dans 24 Go (MoE 30B/3B actifs, rapide, tool-calling). C'est lui qui pilote.
- **Modèle de traduction** : **`qwen3:14b`** (Ollama) — utilisé par `maj_fr.py` pour
  traduire les nouvelles descriptions de sorts. ~1,3 s/sort une fois chargé.
- Ollama tourne sur `http://127.0.0.1:11434`. S'il est éteint : un appel `studio_*`
  le réveille, ou `ollama serve`.

## 2. Ce que fait la MAJ (en une commande)

```bash
cd V:\Project\Ebonhold\github\EbonholdFR-Client\tools
python maj_fr.py                 # détecte, traduit en local, reconstruit, déploie
python maj_fr.py --dry-run       # détecte + traduit + met à jour le fichier central, SANS déployer
python maj_fr.py "D:\ebonhold\Ebonhold"   # forcer le dossier du jeu
```

`maj_fr.py` enchaîne 4 étapes :
1. **Détection** — lit le `Spell.dbc` custom du serveur (`Data\patch-5.MPQ`) et liste les
   descriptions **nouvelles** (pas déjà dans `data/custom_translations.json`, pas du
   contenu Blizzard de base, pas des entrées internes/junk).
2. **Traduction locale** — chaque nouvelle description passe par `qwen3:14b`, qui préserve
   les codes `$s1 / $d / ${...}` et les balises `@..@`. Vérif automatique : si un code
   manque dans la sortie, 1 nouvel essai, sinon on laisse l'anglais (jamais de texte cassé).
3. **Écriture** — les traductions vont dans `data/custom_translations.json` (le fichier central).
4. **Déploiement** — reconstruit `patch-Z.MPQ` + redéploie l'addon `EbonholdFRFix`
   (réutilise le code de `installer/ebonhold_fr_installer.py`), en gardant les réglages mémorisés.

## 3. Prérequis AVANT de lancer

- ✅ La MAJ du **jeu** doit être **finie** (launcher fermé, plus de téléchargement).
- ✅ Le **jeu doit être FERMÉ** (l'étape déploiement écrit `patch-Z.MPQ`).
- ✅ **Référence FR de base** pour la détection : soit le **pack frFR installé**
  (`Data\frFR\*.MPQ`), soit le cache `build\Spell_frFR.dbc` (déjà présent dans ce repo).
  ⚠️ **Sans référence FR, le script REFUSE de tourner** (sinon il prendrait les ~50 000
  sorts Blizzard de base pour du custom et les traduirait tous).
- ⚠️ Pour un **déploiement plein français** (menus/quêtes FR), le **pack frFR doit être
  réinstallé** dans `Data\frFR\` — **chaque grosse MAJ serveur l'efface** (voir §5).

## 4. Après la MAJ

1. **Tester en jeu** : lancer le jeu, vérifier les descriptions (surtout les nouveaux sorts).
2. **Revoir** rapidement les traductions douteuses dans `data/custom_translations.json`
   (le modèle traduit parfois un nom de sort ou une entrée interne — corriger à la main si besoin).
3. **Publier pour les joueurs** (étape à faire avec Claude ou à la main, PAS automatique) :
   recompiler l'exe (`installer/build_exe.bat`) — il embarque le `custom_translations.json`
   à jour — puis commit + nouvelle release GitHub. Règle de Dylan : **rien n'est publié
   sans son GO explicite ET une validation en jeu.**

## 5. Pièges à connaître (essentiels)

1. **Le launcher Ebonhold EFFACE tout ce qui est custom dans `Data\` à chaque MAJ** :
   `patch-Z.MPQ` **et** le pack `Data\frFR\` disparaissent. C'est normal. Il faut
   réinstaller le pack frFR + relancer `maj_fr.py` (ou juste ré-appliquer via l'installateur
   si aucun nouveau sort).
2. **Méthode NON-destructive** : on ne modifie **JAMAIS** `patch-5.MPQ` / `patch-6.MPQ`.
   Le FR va dans un patch **séparé** `patch-Z.MPQ` qui les surcharge.
3. **Encodage = UTF-8** partout (jamais cp1252, sinon les accents cassent l'affichage).
4. **`patch-Z` ne peut PAS surcharger les fichiers d'addon** — c'est pour ça que la forge
   custom est réparée par un **addon séparé** `EbonholdFRFix` (dans `Interface\AddOns\`,
   hors `Data\` → il survit aux MAJ). Il re-ouvre les interfaces custom quand le PNJ
   s'affiche avec son nom français.
5. **Colonnes du `Spell.dbc` 3.3.5a** : Name=136, Desc=170 (colonnes localisées, frFR = +2).
   Si un jour la structure change, `dbc_localize.py` auto-détecte les blocs localisés au
   déploiement, mais la **détection** (`maj_fr.py`) utilise ces offsets fixes.
6. **Noms de sorts custom : laissés en anglais** (cohérence avec les guides) ; on ne
   traduit que les **descriptions**.

## 6. Carte des fichiers

```
EbonholdFR-Client/
├── tools/
│   ├── maj_fr.py            ← LE script de MAJ (détection + traduction locale + déploiement)
│   ├── dbc_localize.py      moteur de fusion .dbc (auto-détecte les colonnes)
│   ├── mpqwrite.py          créateur d'archive MPQ (Python pur)
│   └── extract_*.py         extraction DBC / détection (utilisés en dev)
├── installer/
│   └── ebonhold_fr_installer.py   configurateur + build patch-Z + déploiement addon
├── addon/EbonholdFRFix/     addon compagnon (fix interfaces custom en FR)
├── data/custom_translations.json  ← LES traductions (clé = texte EN → FR)
└── build/Spell_frFR.dbc     cache de la référence FR Blizzard (secours détection ; git-ignoré)
```

## 7. Diagnostic rapide

- `python maj_fr.py --dry-run` → si « 0 nouvelle » : rien à traduire, juste redéployer.
- « STOP : pack frFR introuvable » → réinstaller le pack, ou vérifier `build\Spell_frFR.dbc`.
- « Ollama injoignable » → `ollama serve`, ou un appel `studio_*` pour le réveiller.
- Traductions bizarres → revoir `data/custom_translations.json` ; le modèle local est
  bon mais pas parfait (surtout sur les noms de sorts).
