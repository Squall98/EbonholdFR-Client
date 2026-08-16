# -*- coding: utf-8 -*-
"""MAJ FR EN UN COUP - pilote par l'IA locale (Ollama sur la 5090).

Apres une mise a jour du serveur Ebonhold, ce script fait TOUT :
  1. detecte les NOUVEAUX sorts custom pas encore traduits (dans le patch-5 a jour) ;
  2. les fait traduire par le modele LOCAL (qwen3:14b via Ollama) en preservant les
     codes $s1/$d/${...} ;
  3. ajoute les traductions dans data/custom_translations.json (le fichier central) ;
  4. reconstruit patch-Z.MPQ + redeploie l'addon EbonholdFRFix (via le code de
     l'installateur), en conservant tes reglages memorises.

Usage :
    python maj_fr.py                 # detecte l'install toute seule, mode auto
    python maj_fr.py "D:\\ebonhold\\Ebonhold"
    python maj_fr.py --dry-run       # detecte + traduit, mais NE deploie PAS

Prerequis : Ollama lance (le MCP studio le reveille, ou `ollama serve`) avec
qwen3:14b tire. Le jeu doit etre FERME pour l'etape de deploiement.
"""
import os, sys, json, re, struct, importlib.util

# La console Windows est en cp1252 en mode non-interactif -> crash sur les accents
# dans les print(). On force l'UTF-8 (le fichier de trads, lui, est deja ecrit en UTF-8).
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import mpyq  # noqa: E402

STORE = os.path.join(REPO, "data", "custom_translations.json")
REF_FRFR = os.path.join(REPO, "build", "Spell_frFR.dbc")  # cache Blizzard FR (secours detection)
DBC = r"DBFilesClient\Spell.dbc"
FR_MPQS = ["patch-frFR-3.MPQ", "patch-frFR-2.MPQ", "patch-frFR.MPQ", "locale-frFR.MPQ"]
NAME_COL, DESC_COL = 136, 170          # colonnes localisees du Spell.dbc 3.3.5a

OLLAMA = "http://127.0.0.1:11434/api/chat"
TRAD_MODEL = "qwen3:14b"
SYS_PROMPT = (
    "Tu traduis des descriptions de sorts de World of Warcraft de l'anglais vers le "
    "francais. REGLES STRICTES : garde INTACTS tous les codes comme $s1, $d, $NNNs1, "
    "${...} et les balises @...@. Ne traduis PAS les noms propres de sorts. Reponds "
    "UNIQUEMENT par la traduction francaise, rien d'autre.")

JUNK = re.compile(r'(_|OLD|TEST|DEBUG|UNUSED|DND|\[PH\]|PH\]|zz|QA|Visual|Trigger|'
                  r'Proc Aura|Dummy|placeholder|NPC |Creature|Mount Token)', re.I)
TOKEN_RE = re.compile(r'\$\{[^}]*\}|\$[0-9a-zA-Z]+|@[^@]+@')


# ----------------------------------------------------------------- lecture DBC
def _parse(buf):
    _magic, rc, _fc, rs, _sbs = struct.unpack("<4sIIII", buf[:20])
    return rc, rs, _sbs, 20

def _rec_id(buf, recoff, rs, i):
    return struct.unpack_from("<I", buf, recoff + i * rs)[0]

def _string(buf, sbs, recoff, rc, rs, i, fi):
    off = struct.unpack_from("<I", buf, recoff + i * rs + fi * 4)[0]
    if off <= 0 or off >= sbs:
        return ""
    bs = recoff + rc * rs
    e = buf.find(b"\x00", bs + off)
    return buf[bs + off:e].decode("utf-8", "replace")

def _clean_name(n):
    if not n or len(n) < 2 or JUNK.search(n) or not re.search(r'[A-Za-z]', n):
        return False
    return len(re.sub(r"[A-Za-z' :\-]", "", n)) <= 2


# --------------------------------------------------------------- detection
def detect_untranslated(install, store, log):
    data = os.path.join(install, "Data")
    p5 = os.path.join(data, "patch-5.MPQ")
    if not os.path.exists(p5):
        raise SystemExit("patch-5.MPQ introuvable dans %s (bon dossier Ebonhold ?)" % data)
    custom = mpyq.MPQArchive(p5).read_file(DBC)

    fr_ids = set()
    for m in FR_MPQS:
        fp = os.path.join(data, "frFR", m)
        if not os.path.exists(fp):
            continue
        try:
            frbuf = mpyq.MPQArchive(fp, listfile=False).read_file(DBC)
        except Exception:
            frbuf = None
        if frbuf:
            frc, frs, _sbs, froff = _parse(frbuf)
            fr_ids = {_rec_id(frbuf, froff, frs, i) for i in range(frc)}
            log("Spell.dbc FR de base : %d entrees (pack frFR installe)." % len(fr_ids))
            break

    # Secours : Spell.dbc FR de base mis en cache dans le repo (donnee Blizzard statique).
    # Permet la detection meme quand le pack frFR a ete efface par une MAJ.
    if not fr_ids and os.path.exists(REF_FRFR):
        frbuf = open(REF_FRFR, "rb").read()
        frc, frs, _sbs, froff = _parse(frbuf)
        fr_ids = {_rec_id(frbuf, froff, frs, i) for i in range(frc)}
        log("Spell.dbc FR de base : %d entrees (cache repo build/)." % len(fr_ids))

    if not fr_ids:
        raise SystemExit(
            "STOP : le pack frFR est introuvable/illisible dans %s\\frFR.\n"
            "  Sans le Spell.dbc francais de base, impossible de distinguer le contenu\n"
            "  custom du contenu Blizzard -> on traduirait des milliers de sorts de base.\n"
            "  Reinstalle le pack frFR (launcher / patch FR), FINIS la MAJ du jeu, puis relance."
            % data)

    rc, rs, sbs, off = _parse(custom)
    log("Spell.dbc custom (serveur) : %d entrees." % rc)
    store_descs = set(store.get("descs", {}))
    seen = {}
    for i in range(rc):
        sid = _rec_id(custom, off, rs, i)
        if sid in fr_ids:
            continue
        name = _string(custom, sbs, off, rc, rs, i, NAME_COL)
        desc = _string(custom, sbs, off, rc, rs, i, DESC_COL)
        if not _clean_name(name) or not desc or len(desc) < 6 or ' ' not in desc:
            continue
        if desc in store_descs or '@' in desc:
            continue
        seen.setdefault(desc, {"name": name, "desc": desc})
    return sorted(seen.values(), key=lambda x: x["name"].lower())


# --------------------------------------------------------------- traduction locale
def _tokens(s):
    return TOKEN_RE.findall(s)

def translate_local(text):
    """Traduit via Ollama local. Verifie que les codes sont preserves (1 retry).
    Renvoie None si echec -> on laisse l'anglais plutot que d'ecrire un texte casse."""
    import urllib.request
    payload = json.dumps({
        "model": TRAD_MODEL, "stream": False, "think": False,
        "options": {"temperature": 0.2},
        "messages": [{"role": "system", "content": SYS_PROMPT},
                     {"role": "user", "content": text}],
    }).encode("utf-8")
    want = _tokens(text)
    for _attempt in range(2):
        try:
            req = urllib.request.Request(OLLAMA, data=payload,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                out = json.load(r)["message"]["content"].strip()
        except Exception as e:
            raise SystemExit("Ollama injoignable (%s). Lance-le : `ollama serve` "
                             "ou un appel studio_*. Modele attendu : %s" % (e, TRAD_MODEL))
        out = out.strip().strip('"')
        if all(tok in out for tok in want):
            return out
    return None


# --------------------------------------------------------------- deploiement
def deploy(install, log):
    """Reutilise le code de l'installateur : reconstruit patch-Z + redeploie l'addon,
    en gardant les reglages memorises (sinon plein francais)."""
    inst_path = os.path.join(REPO, "installer", "ebonhold_fr_installer.py")
    spec = importlib.util.spec_from_file_location("inst", inst_path)
    inst = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inst)
    s = inst.load_settings()
    base = s.get("base", "FR") == "FR"
    voices = s.get("voices", "FR") == "FR"
    spells = s.get("spells", "FR") == "FR"
    other = s.get("other", "FR") == "FR"
    log("Deploiement (Jeu=%s Voix=%s Sorts=%s Reput=%s)..." %
        (s.get("base", "FR"), s.get("voices", "FR"), s.get("spells", "FR"), s.get("other", "FR")))
    inst.apply_config(install, base, voices, spells, other, log)


# --------------------------------------------------------------- main
def find_install(argv):
    for a in argv:
        if not a.startswith("-"):
            return a
    for drive in "CDEFGH":
        for sub in (r"\ebonhold\Ebonhold", r"\Ebonhold", r"\Games\Ebonhold"):
            p = drive + ":" + sub
            if os.path.exists(os.path.join(p, "Data", "patch-5.MPQ")):
                return p
    return ""

def main():
    dry = "--dry-run" in sys.argv
    install = find_install(sys.argv[1:])
    if not install:
        raise SystemExit("Install Ebonhold introuvable. Passe le dossier en argument : "
                         'python maj_fr.py "D:\\ebonhold\\Ebonhold"')
    log = lambda m: print("  " + m, flush=True)
    print("== MAJ FR Ebonhold ==  install :", install)

    store = json.load(open(STORE, encoding="utf-8"))
    store.setdefault("names", {}); store.setdefault("descs", {})

    print("\n[1/4] Detection des nouveaux sorts a traduire...")
    todo = detect_untranslated(install, store, log)
    print("  -> %d description(s) nouvelle(s) a traduire." % len(todo))

    if todo:
        print("\n[2/4] Traduction en local (qwen3:14b sur la 5090)...")
        ok = fail = 0
        def _save():
            json.dump(store, open(STORE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        for k, item in enumerate(todo, 1):
            fr = translate_local(item["desc"])
            if fr:
                store["descs"][item["desc"]] = fr
                ok += 1
                print("  [%d/%d] %-28s -> %s" % (k, len(todo), item["name"][:28], fr[:60]))
            else:
                fail += 1
                print("  [%d/%d] %-28s -> ECHEC (codes non preserves, laisse en EN)" %
                      (k, len(todo), item["name"][:28]))
            if k % 25 == 0:      # sauvegarde incrementale (un run long ne perd rien)
                _save()
        print("\n[3/4] Ecriture du fichier central (%d ajout, %d echec)..." % (ok, fail))
        _save()
        print("  -> data/custom_translations.json mis a jour (%d descriptions au total)."
              % len(store["descs"]))
    else:
        print("\n[2-3/4] Rien de nouveau a traduire, le fichier central est deja complet.")

    if dry:
        print("\n[4/4] --dry-run : deploiement SAUTE. Relance sans --dry-run pour appliquer.")
        return
    print("\n[4/4] Reconstruction de patch-Z + addon (jeu FERME requis)...")
    deploy(install, log)
    print("\nTERMINE. Lance le jeu, verifie en jeu (surtout les nouveaux sorts).")

if __name__ == "__main__":
    main()
