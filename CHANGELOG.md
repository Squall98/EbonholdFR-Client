# Changelog

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
