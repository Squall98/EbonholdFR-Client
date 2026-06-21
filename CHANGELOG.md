# Changelog

## v2.0 — méthode patch-Z (non-destructive)
- **Nouvelle méthode** : le français est injecté dans un patch **séparé** `patch-Z.MPQ`
  qui surcharge `patch-5/6` **sans les modifier**.
  → compatible launcher, **survit aux mises à jour** du serveur (fini le « not up to date »).
- **Configurateur** avec profils de langue : Tout français / Jeu anglais + contenu français / Anglais.
- Le client **anglais** affiche aussi les accents UTF-8 → profil « contenu FR » possible **sans le pack** frFR.
- Switch FR/EN = ajouter/retirer `patch-Z` + changer la langue.

## v1 — méthode in-place (dépréciée)
- Injection directe dans `patch-5/6` (cassait après chaque mise à jour du serveur).
