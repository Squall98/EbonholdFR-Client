# Changelog

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
