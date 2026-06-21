# EbonholdFR — Client (traduction française)

Met le client **Project Ebonhold** (World of Warcraft 3.3.5a, rogue-lite) **en français** : sorts, talents, echoes, factions, compétences, hauts faits, titres… et le jeu de base (menus, quêtes, zones) avec le pack de langue.

Méthode **non-destructive** : le français est injecté dans un patch **séparé** (`patch-Z.MPQ`) qui surcharge les fichiers du serveur **sans les modifier**. → compatible launcher, **survit aux mises à jour** du serveur, switch FR/EN instantané.

---

## 🟢 Installation (l'exe, sans Python)

> 🔰 **Débutant ?** Suis le guide illustré pas-à-pas : **[GUIDE-INSTALLATION.md](GUIDE-INSTALLATION.md)**.

1. Télécharge **`EbonholdFR-Installer.exe`** (dans les *Releases*).
2. **Ferme le jeu**, puis double-clique sur l'exe.
3. Choisis ton dossier Ebonhold (celui qui contient `Wow.exe`) — souvent détecté tout seul.
4. Règle chaque **catégorie** en FR/EN (ou bouton **« Tout en français »**) et clique sur **Appliquer**.
5. Lance le jeu.

> ⚠️ Windows peut afficher un avertissement bleu (« Windows a protégé votre ordinateur ») pour un programme non signé : clique sur **Informations complémentaires → Exécuter quand même**.

### Les réglages (chacun Français / Anglais)

| Réglage | Couvre | Pack frFR requis |
|---|---|---|
| **Jeu** | interface, menus, quêtes, zones | oui pour FR (~2,4 Go) |
| **Voix** | doublages (seulement si Jeu = FR) | — |
| **Sorts, talents & echoes** | la base de données des sorts | non |
| **Réputations, hauts faits & titres** | le reste du contenu | non |

Un bouton **« Tout en français »** règle tout d'un coup. Exemples : *Jeu FR + Voix EN* (texte français, voix anglaises), *Jeu EN + Sorts FR* (jeu anglais, sorts français)…

> ⚠️ **interface / menus / quêtes** sont **un seul réglage** (« Jeu ») : c'est une limite du moteur de WoW (une seule langue pour tout ce bloc). Seuls les **voix** et le **contenu** (sorts, réputations…) sont séparables.

Mettre le **Jeu** en français nécessite le **pack de langue frFR** (les menus/quêtes vivent dedans). L'installeur te prévient s'il manque et ouvre la page de téléchargement.

📥 **Pack frFR** : [Télécharger (Google Drive)](https://drive.google.com/file/d/1j3OuTz1KMUsuUWXQiMJaE0yQXmAobRxu/view) — décompresse l'archive et place le dossier **`frFR`** dans le **`Data`** de ton client, puis relance l'installeur.

---

## Pourquoi ça marche (et pourquoi c'est solide)

Ebonhold remplit seulement la colonne **anglaise** de ses fichiers de données (`.dbc`). On y injecte le français par-dessus, mais **dans un patch séparé** :

- `patch-Z.MPQ` est chargé par le client **après** `patch-5/6` et les **surcharge** — sans toucher aux originaux.
- Donc le launcher ne voit **aucun fichier modifié** → pas d'erreur « not up to date », et le français **survit aux mises à jour** du serveur.
- Le **switch FR/EN** revient juste à ajouter/retirer `patch-Z` + changer la langue.

Priorité des textes : **nos traductions** (custom) > **français de base Blizzard** (pack) > anglais.

---

## Mettre à jour après un patch du serveur

1. Lance le **launcher officiel** d'Ebonhold pour mettre à jour le jeu.
2. **Relance l'installeur** et clique sur **Appliquer** (il reconstruit `patch-Z` à partir des nouveaux fichiers).

---

## Pour les développeurs (méthode manuelle)

Prérequis : **Python 3** + **mpyq** (`pip install mpyq`).

```bash
cp config.example.py config.py     # renseigne SRC_DATA / DST_DATA (= le Data de ton client)
cd tools
python extract_base_dbc.py         # extrait les Spell.dbc de référence
python build_patchz.py             # construit patch-Z.MPQ (FR), sans toucher patch-5/6
```

`build_patchz.py` accepte la colonne cible : `frFR` (jeu en français, avec pack) ou `enUS` (jeu anglais + contenu FR, sans pack).

### Ajouter / corriger une traduction

Tout vit dans **`data/custom_translations.json`** (clé = texte anglais **exact**, valeur = français ; préserve les codes `$s1`, `$d`, `${...}`). Puis relance `build_patchz.py`.

---

## Structure

```
EbonholdFR-Client/
├── installer/
│   ├── ebonhold_fr_installer.py   # configurateur (interface + profils)
│   └── build_exe.bat              # compile l'exe autonome
├── data/custom_translations.json  # LES traductions (EN → FR)
├── tools/
│   ├── dbc_localize.py            # moteur de fusion .dbc (colonne enUS ou frFR)
│   ├── mpqwrite.py                # créateur d'archive MPQ en Python pur
│   ├── build_patchz.py            # construit patch-Z.MPQ
│   ├── extract_base_dbc.py        # extrait les DBC de référence
│   ├── extract_custom_spells.py   # liste ce qui reste à traduire
│   └── auto_translate.py          # traductions par motifs (montures, tomes…)
├── COMMENT-PUBLIER.md             # guide GitHub pas-à-pas
├── LICENSE  ·  CHANGELOG.md
```

---

## Détails techniques

- **`.dbc`** WotLK 3.3.5a (WDBC). Colonnes localisées détectées automatiquement ; français écrit dans le slot **frFR** (`+2`) ou **enUS** (`+0`) selon le profil.
- **Encodage UTF-8** (le client Ebonhold — y compris en anglais — affiche bien les accents UTF-8).
- **MPQ** : `mpqwrite.py` crée des archives MPQ v1 (secteurs zlib) lisibles par le client 3.3.5a, sans dépendance externe.
- **`patch-Z.MPQ`** : patch racine chargé après `patch-5/6`, qu'il surcharge sans les modifier.

---

## Limites

- **Noms d'objets / quêtes / PNJ custom** : envoyés par le serveur, pas dans un `.dbc` → restent en anglais.
- **Noms** des sorts/echoes custom : laissés en anglais (cohérence avec les guides) ; seules les **descriptions** sont traduites.

---

## Crédits & avertissement

Réalisé par **Squall98**. Projet communautaire **non officiel**, sans affiliation avec Blizzard Entertainment ni Project Ebonhold. Aucun fichier de jeu n'est redistribué. Sous licence MIT.

> 📖 Pour publier/mettre à jour ce dépôt sur GitHub : **[COMMENT-PUBLIER.md](COMMENT-PUBLIER.md)**.
