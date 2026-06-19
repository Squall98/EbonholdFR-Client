# Changelog

## v1.0
- Traduction française complète du **client** Project Ebonhold (WotLK 3.3.5a).
- Injection des textes FR dans les `.dbc` custom du serveur :
  - **Spell.dbc** (`patch-5`) : sorts, talents, echoes.
  - **patch-6** : factions/réputations, compétences, hauts faits, titres, enchantements.
- Stratégie de fusion : nos traductions > français de base Blizzard > anglais (jamais de texte vide).
- **672 descriptions de sorts custom** traduites à la main + montures/tomes par motifs auto.
- Créateur d'archive MPQ en Python pur (secteurs zlib, compatible client 3.3.5a).
- Encodage de sortie **UTF-8** (attendu par le client Ebonhold).
- Pipeline de mise à jour en une commande (`rebuild_all.py`).
