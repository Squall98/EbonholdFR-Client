# -*- coding: utf-8 -*-
"""Auto-traduit par motifs deterministes les entrees de build/todo.json (montures,
vitesses, tomes, lignes mecaniques simples) et les ajoute a data/custom_translations.json.
Ne touche jamais aux codes $s1/$d/$t ni aux tokens @..@. A lancer apres extract_custom_spells.py."""
import os, re, json
from _common import STORE, BUILD_DIR

DESC_PATTERNS = [
    (r'^Summons and dismisses a rideable (.+?)\.?$', lambda m: "Invoque et renvoie %s." % m.group(1)),
    (r'^Summons and dismisses your (.+?)\.?$', lambda m: "Invoque et renvoie votre %s." % m.group(1)),
    (r'^Increases your speed by (\$s\d+)%\.?$', lambda m: "Augmente votre vitesse de %s%%." % m.group(1)),
    (r'^Increases ground speed by (\$s\d+)%\. Increases flying speed by (\$s\d+)%\.?$',
        lambda m: "Augmente la vitesse au sol de %s%%. Augmente la vitesse de vol de %s%%." % (m.group(1), m.group(2))),
    (r'^Increases ground speed by (\$s\d+)%\.?$', lambda m: "Augmente la vitesse au sol de %s%%." % m.group(1)),
    (r'^Increases flying speed by (\$s\d+)%\.?$', lambda m: "Augmente la vitesse de vol de %s%%." % m.group(1)),
    (r'^Apprentice Riding\.?$', lambda m: "Monte (apprenti)."),
    (r'^Journeyman Riding\.?$', lambda m: "Monte (compagnon)."),
    (r'^Expert Riding\.?$', lambda m: "Monte (expert)."),
    (r'^Artisan Riding\.?$', lambda m: "Monte (artisan)."),
    (r'^Master Riding\.?$', lambda m: "Monte (maitre)."),
    (r'^Slow And Steady\.\.\.$', lambda m: "Lentement mais surement..."),
    (r'^Deal damage\.?$', lambda m: "Inflige des degats."),
    (r'^Find targets\.?$', lambda m: "Cible des ennemis."),
    (r'^Grants you the ability to discover (.+?) when offered new Echoes\.?$',
        lambda m: "Vous octroie la capacite de decouvrir %s quand de nouveaux Echoes vous sont proposes." % m.group(1)),
]

def try_desc(d):
    for pat, fn in DESC_PATTERNS:
        m = re.match(pat, d.strip())
        if m:
            return fn(m)
    return None

def main():
    todo = json.load(open(os.path.join(BUILD_DIR, "todo.json"), encoding="utf-8"))
    store = json.load(open(STORE, encoding="utf-8")) if os.path.exists(STORE) else {"names": {}, "descs": {}}
    store.setdefault("names", {}); store.setdefault("descs", {})
    n = 0
    for u in todo:
        d = u["desc"]
        if d in store["descs"]:
            continue
        fr = try_desc(d)
        if fr:
            store["descs"][d] = fr
            n += 1
    json.dump(store, open(STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Descriptions auto-traduites ajoutees :", n)
    print("Total store -> noms:%d descs:%d" % (len(store["names"]), len(store["descs"])))

if __name__ == "__main__":
    main()
