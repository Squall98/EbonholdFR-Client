# -*- coding: utf-8 -*-
"""SCRIPT PRINCIPAL : (re)construit le client FR.
Lit les patchs de texte PRISTINE depuis le client original (SRC_DATA), injecte le
francais (traductions du fichier central > FR de base Blizzard > anglais) et reecrit
les patchs traduits dans le client FR (DST_DATA). Encodage de sortie : UTF-8.

A relancer apres chaque mise a jour du serveur (le client doit etre FERME).

Usage : python rebuild_all.py
"""
import os, json, mpyq
from _common import SRC_DATA, DST_DATA, STORE
import mpqwrite, dbc_localize

FR_MPQS = ["patch-frFR-3.MPQ", "patch-frFR-2.MPQ", "patch-frFR.MPQ", "locale-frFR.MPQ"]
TEXT_PATCHES = ["patch-5.MPQ", "patch-6.MPQ"]   # patchs contenant des .dbc de texte

def main():
    # 1) fichier central de traductions (cle = texte EN -> FR)
    store = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {}
    tr = {}
    tr.update(store.get("names", {}))
    tr.update(store.get("descs", {}))
    print("Traductions chargees :", len(tr))

    # 2) archives FR de base (lecture seule) pour le texte Blizzard
    fr_arch = []
    for m in FR_MPQS:
        fp = os.path.join(DST_DATA, "frFR", m)
        if os.path.exists(fp):
            try:
                fr_arch.append(mpyq.MPQArchive(fp, listfile=False))
            except Exception:
                pass

    def find_base(path):
        for a in fr_arch:
            try:
                d = a.read_file(path)
                if d:
                    return d
            except Exception:
                pass
        return None

    # 3) reconstruit chaque patch de texte
    for patch in TEXT_PATCHES:
        sp = os.path.join(SRC_DATA, patch)
        dp = os.path.join(DST_DATA, patch)
        if not os.path.exists(sp):
            print("  (%s absent de la source, ignore)" % patch)
            continue
        a = mpyq.MPQArchive(sp)
        names = [n for n in a.read_file("(listfile)").decode("latin-1")
                 .replace("\r\n", "\n").split("\n") if n.strip()]
        out = {}
        print("\n[%s] %d fichiers" % (patch, len(names)))
        for n in names:
            raw = a.read_file(n)
            if not n.lower().endswith(".dbc"):
                out[n] = raw
                continue
            base = find_base(n)
            try:
                merged, st = dbc_localize.merge(raw, base, tr)
            except Exception as e:
                merged, st = None, {"err": str(e)[:30]}
            if merged and st.get("blocks"):
                out[n] = merged
                print("   %-32s tr=%d base=%d EN=%d" %
                      (os.path.basename(n), st["from_tr"], st["from_base"], st["copied_en"]))
            else:
                out[n] = raw
        sz = mpqwrite.create_mpq(dp, out)
        print("   -> %s ecrit (%.1f Mo)" % (patch, sz / 1024 / 1024))

    print("\nTERMINE. Client FR reconstruit dans", DST_DATA)
    print("Pour voir les nouveaux textes a traduire : python extract_custom_spells.py")

if __name__ == "__main__":
    main()
