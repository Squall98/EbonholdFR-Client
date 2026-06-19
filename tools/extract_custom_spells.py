# -*- coding: utf-8 -*-
"""Liste les descriptions de sorts custom NON encore traduites (a la main).
Exclut : sorts deja FR de base Blizzard, echoes couverts par l'addon EbonholdFR
(si ADDON_DATA renseigne), textes deja dans le fichier central, tokens @..@.
Sortie : build/todo.json + un apercu console. A lancer apres extract_base_dbc.py."""
import os, re, json, struct
from _common import ADDON_DATA, STORE, BUILD_DIR

NAME, DESC = 136, 170   # colonnes localisees (Name / Description) du Spell.dbc 3.3.5a
JUNK = re.compile(r'(_|OLD|TEST|DEBUG|UNUSED|DND|\[PH\]|PH\]|zz|QA|Visual|Trigger|'
                  r'Proc Aura|Dummy|placeholder|NPC |Creature|Mount Token)', re.I)

def load(fn):
    buf = open(os.path.join(BUILD_DIR, fn), "rb").read()
    _m, rc, _fc, rs, sbs = struct.unpack("<4sIIII", buf[:20])
    return buf, rc, rs, sbs, 20

def gs(buf, sbs, recoff, rc, rs, i, fi):
    off = struct.unpack_from("<I", buf, recoff + i*rs + fi*4)[0]
    if off <= 0 or off >= sbs:
        return ""
    bs = recoff + rc*rs
    e = buf.find(b"\x00", bs + off)
    return buf[bs+off:e].decode("utf-8", "replace")

def clean_name(n):
    if not n or len(n) < 2 or JUNK.search(n) or not re.search(r'[A-Za-z]', n):
        return False
    return len(re.sub(r"[A-Za-z' :\-]", "", n)) <= 2

def main():
    cb, crc, crs, csbs, croff = load("Spell_custom.dbc")
    fb, frc, frs, fsbs, froff = load("Spell_frFR.dbc")

    fr_ids = {struct.unpack_from("<I", fb, froff + i*frs)[0] for i in range(frc)}

    addon_ids = set()
    if ADDON_DATA and os.path.exists(ADDON_DATA):
        txt = open(ADDON_DATA, encoding="utf-8").read()
        addon_ids = {int(x) for x in re.findall(r'b\[(\d+)\]', txt)}
        print("ids couverts par l'addon (exclus) :", len(addon_ids))

    store_descs = set()
    if os.path.exists(STORE):
        store_descs = set(json.load(open(STORE, encoding="utf-8")).get("descs", {}))

    seen = {}
    for i in range(crc):
        sid = struct.unpack_from("<I", cb, croff + i*crs)[0]
        if sid in fr_ids or sid in addon_ids:
            continue
        name = gs(cb, csbs, croff, crc, crs, i, NAME)
        desc = gs(cb, csbs, croff, crc, crs, i, DESC)
        if not clean_name(name) or not desc or len(desc) < 6 or ' ' not in desc:
            continue
        if desc in store_descs or '@' in desc:
            continue
        seen.setdefault((name, desc), {"name": name, "desc": desc, "ids": []})["ids"].append(sid)

    todo = sorted(seen.values(), key=lambda x: x["name"].lower())
    json.dump(todo, open(os.path.join(BUILD_DIR, "todo.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("A traduire (uniques) :", len(todo))
    for u in todo[:25]:
        print("  [%s] %s" % (u["name"], u["desc"][:70].replace("\n", " ")))
    if todo:
        print("\n-> Ajoute les traductions dans data/custom_translations.json (cle=texte EN -> FR),")
        print("   puis relance : python rebuild_all.py")

if __name__ == "__main__":
    main()
