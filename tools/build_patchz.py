# -*- coding: utf-8 -*-
"""Construit patch-Z.MPQ : patch SEPARE qui surcharge patch-5/6 avec le francais,
SANS les modifier (compatible launcher, survit aux MAJ serveur).

  python build_patchz.py          -> francais dans la colonne frFR (jeu en frFR, avec pack)
  python build_patchz.py --enus   -> francais dans la colonne enUS (jeu en anglais, sans pack)

Le jeu doit etre FERME. patch-Z.MPQ est ecrit dans DST_DATA.
"""
import os, sys, json, mpyq
from _common import DST_DATA, STORE
import mpqwrite, dbc_localize

FR_MPQS = ["patch-frFR-3.MPQ", "patch-frFR-2.MPQ", "patch-frFR.MPQ", "locale-frFR.MPQ"]
TEXT_PATCHES = ["patch-5.MPQ", "patch-6.MPQ"]

def main():
    fr_col = 0 if "--enus" in sys.argv else 2
    store = json.load(open(STORE, encoding="utf-8"))
    tr = {}; tr.update(store.get("names", {})); tr.update(store.get("descs", {}))
    print("Traductions :", len(tr), "| colonne cible :", "enUS" if fr_col == 0 else "frFR")

    fr_arch = []
    for m in FR_MPQS:
        p = os.path.join(DST_DATA, "frFR", m)
        if os.path.exists(p):
            try: fr_arch.append(mpyq.MPQArchive(p, listfile=False))
            except Exception: pass
    def find_base(path):
        for a in fr_arch:
            try:
                d = a.read_file(path)
                if d: return d
            except Exception: pass
        return None

    patchz = {}
    for patch in TEXT_PATCHES:
        sp = os.path.join(DST_DATA, patch)
        if not os.path.exists(sp):
            print("  (%s absent)" % patch); continue
        a = mpyq.MPQArchive(sp)
        names = [n for n in a.read_file("(listfile)").decode("latin-1")
                 .replace("\r\n", "\n").split("\n") if n.strip()]
        for n in names:
            if not n.lower().endswith(".dbc"):
                continue
            raw = a.read_file(n)
            base = find_base(n)
            try:
                merged, st = dbc_localize.merge(raw, base, tr, fr_col=fr_col)
            except Exception:
                merged = None
            if merged:
                patchz[n] = merged
                print("  %-30s tr=%d base=%d EN=%d" % (os.path.basename(n), st["from_tr"], st["from_base"], st["copied_en"]))

    out = os.path.join(DST_DATA, "patch-Z.MPQ")
    sz = mpqwrite.create_mpq(out, patchz)
    print("\npatch-Z.MPQ ecrit : %.1f Mo, %d DBC -> %s" % (sz/1024/1024, len(patchz), out))
    print("patch-5/6 NON modifies. Pense a regler Config.wtf (SET locale frFR ou enUS).")

if __name__ == "__main__":
    main()
