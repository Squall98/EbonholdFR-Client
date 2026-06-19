# -*- coding: utf-8 -*-
"""Extrait les Spell.dbc necessaires a la fusion, dans build/ :
  - Spell_custom.dbc : version custom du serveur (anglais)  -> depuis SRC_DATA/patch-5.MPQ
  - Spell_frFR.dbc   : version francaise de Blizzard         -> depuis DST_DATA/frFR/*.MPQ
A lancer une fois (et apres chaque mise a jour du serveur)."""
import os, mpyq, struct
from _common import SRC_DATA, DST_DATA, BUILD_DIR

CUSTOM_PATCH = "patch-5.MPQ"   # contient le Spell.dbc custom du serveur
FR_MPQS = ["patch-frFR-3.MPQ", "patch-frFR-2.MPQ", "patch-frFR.MPQ", "locale-frFR.MPQ"]
DBC = r"DBFilesClient\Spell.dbc"

def main():
    # 1) Spell.dbc custom (anglais)
    p = os.path.join(SRC_DATA, CUSTOM_PATCH)
    data = mpyq.MPQArchive(p).read_file(DBC)
    open(os.path.join(BUILD_DIR, "Spell_custom.dbc"), "wb").write(data)
    print("Spell_custom.dbc :", len(data), "octets (depuis %s)" % CUSTOM_PATCH)

    # 2) Spell.dbc francais de base (le plus prioritaire trouve)
    frdir = os.path.join(DST_DATA, "frFR")
    for m in FR_MPQS:
        fp = os.path.join(frdir, m)
        if not os.path.exists(fp):
            continue
        try:
            d = mpyq.MPQArchive(fp, listfile=False).read_file(DBC)
        except Exception:
            d = None
        if d:
            open(os.path.join(BUILD_DIR, "Spell_frFR.dbc"), "wb").write(d)
            print("Spell_frFR.dbc   :", len(d), "octets (depuis %s)" % m)
            return
    print("ATTENTION : Spell.dbc francais introuvable dans frFR/ (locale frFR installee ?)")

if __name__ == "__main__":
    main()
