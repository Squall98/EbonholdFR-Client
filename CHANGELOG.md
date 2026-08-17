# Changelog

## v2.4 — echoes & skill tree en français + fix métiers
- **Noms ET descriptions traduits** pour les echoes, l'arbre de compétences et les
  affixes (fichier central : **1855 noms + 2422 descriptions**), y compris les
  descriptions à token (`@flat40@`, `$s1`) et les nœuds « X (Rank N) ».
- **Fenêtre Métiers en français** (Minage, Forge, Cuisine…) : l'installateur injecte
  dans `patch-Z` une version FR de `SpellBookFrame.lua` (noms de métiers + garde
  anti-taint) et de `TalentDatabase.lua` (descriptions génériques du skill tree).
- Reste en anglais (limites connues) : le « chrome » de l'UI custom protégée
  (onglets, « Rank », « Soul Ashes »…) et les descriptions envoyées par le serveur.

## v2.3 — compatibilité grosse MAJ serveur + 968 nouveaux sorts traduits
- **968 nouveaux sorts/echoes/affixes** custom ajoutés par la grosse mise à jour du serveur,
  **traduits** et intégrés (fichier central : 1760 descriptions au total).
- Patch régénéré à partir des nouveaux `patch-5/6` → **compatible avec la nouvelle version**
  du serveur (les descriptions FR disparues sont de retour).
- Nouvel outil `tools/maj_fr.py` : régénère le patch et **traduit les nouveautés en local**
  (Ollama / qwen3:14b), pour des mises à jour rapides après chaque patch serveur.

## v2.2 — réparation auto après mise à jour serveur + notif de version
- **Réparation en 1 clic** : au lancement, si le patch FR a été **effacé par une mise à jour
  du serveur** (le launcher supprime `patch-Z.MPQ`), l'installateur le détecte et affiche
  **« Réparer maintenant »** — un clic remet le français (tes derniers réglages sont mémorisés).
- **Réglages mémorisés** : l'installateur retient ton dossier et tes choix (Jeu/Voix/Sorts/Réput)
  et les pré-remplit au prochain lancement.
- **Notification de version** : l'installateur vérifie GitHub et prévient si une nouvelle
  version est disponible (bouton pour la télécharger).

## v2.1 — fix interfaces custom en jeu français
- **Addon compagnon `EbonholdFRFix`** déployé automatiquement par l'installateur
  dans `Interface\AddOns\` (hors de `Data\` → **survit aux mises à jour** serveur).
- Corrige la **forge (Enclume enchantée / extraction d'affixes)** qui ne s'ouvrait pas
  en français : l'addon d'Ebonhold ne reconnaissait que le nom **anglais** du PNJ.
  L'addon compagnon re-déclenche l'interface quand il voit le nom **français**.
- Purement additif : aucun fichier d'Ebonhold modifié, aucun effet sur un client anglais.
- Commande `/frfix` (diagnostic) pour capturer le nom FR d'un PNJ custom.

## v2.0 — méthode patch-Z (non-destructive) + configurateur
- **Nouvelle méthode** : le français est injecté dans un patch **séparé** `patch-Z.MPQ`
  qui surcharge `patch-5/6` **sans les modifier**.
  → compatible launcher, **survit aux mises à jour** du serveur (fini le « not up to date »).
- **Configurateur** avec 4 réglages indépendants (chacun FR/EN) : **Jeu** (interface/menus/quêtes),
  **Voix**, **Sorts/talents/echoes**, **Réputations/hauts faits/titres** + bouton « Tout en français ».
- **Voix** séparables : texte FR + voix EN possible (échange des fichiers `speech-*.MPQ`, réversible).
- Le client **anglais** affiche aussi les accents UTF-8 → contenu FR possible **sans le pack** frFR.
- Icône de l'application.

## v1 — méthode in-place (dépréciée)
- Injection directe dans `patch-5/6` (cassait après chaque mise à jour du serveur).
