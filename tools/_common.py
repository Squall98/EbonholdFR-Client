# -*- coding: utf-8 -*-
"""Chemins partages par les outils. Lit config.py (a creer depuis config.example.py)."""
import os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

try:
    import config
except ImportError:
    raise SystemExit(
        "[config manquante] Copie 'config.example.py' en 'config.py' "
        "et renseigne SRC_DATA / DST_DATA."
    )

SRC_DATA = config.SRC_DATA                      # client original (lecture)
DST_DATA = config.DST_DATA                      # client FR (ecriture)
ADDON_DATA = getattr(config, "ADDON_DATA", None)

DATA_DIR = os.path.join(REPO, "data")           # versionne : custom_translations.json
BUILD_DIR = os.path.join(REPO, "build")         # ignore par git : DBC extraits, todo.json
os.makedirs(BUILD_DIR, exist_ok=True)

STORE = os.path.join(DATA_DIR, "custom_translations.json")  # FICHIER CENTRAL des traductions
