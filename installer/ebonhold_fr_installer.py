# -*- coding: utf-8 -*-
"""EbonholdFR - Configurateur de langue (interface graphique).

Methode NON-DESTRUCTIVE : le francais est injecte dans un patch SEPARE 'patch-Z.MPQ'
qui surcharge patch-5/6 SANS les modifier (compatible launcher, survit aux MAJ).

Reglages :
  - Jeu (interface/menus/quetes/zones/voix) : FR/EN   <- 1 seul reglage (limite moteur WoW)
  - Sorts / talents / echoes                : FR/EN   (independant)
  - Reputations / hauts faits / titres      : FR/EN   (independant)
"""
import os, sys, json, threading, webbrowser, shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def resource(rel):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, rel)
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", rel))

sys.path.insert(0, resource("tools"))
import mpqwrite, dbc_localize  # noqa: E402
import mpyq  # noqa: E402

STORE_PATH = resource("data/custom_translations.json")
PACK_URL = "https://drive.google.com/file/d/1j3OuTz1KMUsuUWXQiMJaE0yQXmAobRxu/view"
FR_MPQS = ["patch-frFR-3.MPQ", "patch-frFR-2.MPQ", "patch-frFR.MPQ", "locale-frFR.MPQ"]
TEXT_PATCHES = ["patch-5.MPQ", "patch-6.MPQ"]

def load_tr():
    s = json.load(open(STORE_PATH, encoding="utf-8"))
    tr = {}; tr.update(s.get("names", {})); tr.update(s.get("descs", {}))
    return tr

def find_ebonhold():
    for drive in "CDEFGH":
        for sub in (r"\ebonhold\Ebonhold", r"\Ebonhold", r"\Games\Ebonhold",
                    r"\Program Files\Ebonhold", r"\Program Files (x86)\Ebonhold"):
            p = drive + ":" + sub
            if os.path.exists(os.path.join(p, "Data", "patch-5.MPQ")):
                return p
    return ""

def has_pack(data_dir):
    return os.path.exists(os.path.join(data_dir, "frFR", "locale-frFR.MPQ"))

def set_locale(install_dir, locale):
    cfg = os.path.join(install_dir, "WTF", "Config.wtf")
    lines = open(cfg, encoding="latin-1").read().splitlines() if os.path.exists(cfg) else []
    out, found = [], False
    for ln in lines:
        if ln.strip().upper().startswith("SET LOCALE"):
            out.append('SET locale "%s"' % locale); found = True
        else:
            out.append(ln)
    if not found:
        out.insert(0, 'SET locale "%s"' % locale)
    os.makedirs(os.path.dirname(cfg), exist_ok=True)
    open(cfg, "w", encoding="latin-1").write("\n".join(out) + "\n")

def fix_realmlist(data_dir):
    en = os.path.join(data_dir, "enUS", "realmlist.wtf")
    fr = os.path.join(data_dir, "frFR", "realmlist.wtf")
    if os.path.exists(en) and os.path.isdir(os.path.dirname(fr)):
        shutil.copy2(en, fr)

def remove_patchz(data_dir):
    p = os.path.join(data_dir, "patch-Z.MPQ")
    if os.path.exists(p):
        os.remove(p)

def deploy_addon(install_dir, log):
    """Installe l'addon compagnon EbonholdFRFix dans Interface\\AddOns.
    Il reactive les interfaces custom (forge...) quand un PNJ s'affiche avec son nom
    francais. Purement additif, sans effet en anglais. Place hors de Data\\ -> le
    launcher n'y touche pas (survit aux mises a jour serveur)."""
    src = resource(os.path.join("addon", "EbonholdFRFix"))
    if not os.path.isdir(src):
        return
    dst = os.path.join(install_dir, "Interface", "AddOns", "EbonholdFRFix")
    try:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isdir(dst):
            shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        log("Addon EbonholdFRFix installe (forge custom OK en francais).")
    except Exception as e:
        log("Addon non installe (%s)." % e)

# Fichiers de voix : nom frFR <- source enUS
SPEECH = [
    ("speech-frFR.MPQ", "speech-enUS.MPQ"),
    ("lichking-speech-frFR.MPQ", "lichking-speech-enUS.MPQ"),
    ("expansion-speech-frFR.MPQ", "expansion-speech-enUS.MPQ"),
]

def manage_voices(data_dir, voices_fr, log):
    """Voix FR = fichiers du pack frFR. Voix EN = on copie les voix anglaises sous le nom frFR
    (sauvegarde des voix FR en .fr-backup pour pouvoir revenir)."""
    frdir = os.path.join(data_dir, "frFR")
    endir = os.path.join(data_dir, "enUS")
    for frname, enname in SPEECH:
        frp = os.path.join(frdir, frname)
        bak = frp + ".fr-backup"
        enp = os.path.join(endir, enname)
        if voices_fr:
            if os.path.exists(bak):
                if os.path.exists(frp):
                    os.remove(frp)
                os.rename(bak, frp)
                log("Voix FR restaurees : %s" % frname)
        else:
            if os.path.exists(enp):
                if os.path.exists(frp) and not os.path.exists(bak):
                    os.rename(frp, bak)            # sauvegarde des voix FR
                log("Copie voix anglaises -> %s (peut prendre 1 min)..." % frname)
                shutil.copy2(enp, frp)

def group_of(dbc_name):
    return "spells" if dbc_name.lower().endswith("spell.dbc") else "other"

def build_patchz(data_dir, base_fr, spells_fr, other_fr, log):
    """Construit patch-Z selon la langue voulue par groupe.
    frFR (base_fr) : tous les DBC dans patch-Z (FR traduit, ou EN recopie).
    enUS           : seulement les groupes en FR (colonne enUS)."""
    fr_col = 2 if base_fr else 0
    tr = load_tr()
    want = {"spells": spells_fr, "other": other_fr}
    fr_arch = []
    if base_fr:
        for m in FR_MPQS:
            p = os.path.join(data_dir, "frFR", m)
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
        sp = os.path.join(data_dir, patch)
        if not os.path.exists(sp):
            continue
        a = mpyq.MPQArchive(sp)
        names = [n for n in a.read_file("(listfile)").decode("latin-1")
                 .replace("\r\n", "\n").split("\n") if n.strip()]
        for n in names:
            if not n.lower().endswith(".dbc"):
                continue
            g_fr = want[group_of(n)]
            if not base_fr and not g_fr:
                continue   # enUS + groupe EN -> rien a faire (l'anglais d'origine s'affiche)
            raw = a.read_file(n)
            use_base = base_fr and g_fr
            use_tr = tr if g_fr else {}
            base = find_base(n) if use_base else None
            try:
                merged, _ = dbc_localize.merge(raw, base, use_tr, fr_col=fr_col)
            except Exception:
                merged = None
            if merged:
                patchz[n] = merged
    if patchz:
        mpqwrite.create_mpq(os.path.join(data_dir, "patch-Z.MPQ"), patchz)
        log("patch-Z.MPQ ecrit (%d fichiers)." % len(patchz))
    else:
        remove_patchz(data_dir); log("patch-Z retire (rien a traduire).")

def apply_config(install_dir, base_fr, voices_fr, spells_fr, other_fr, log):
    data = os.path.join(install_dir, "Data")
    if base_fr:
        fix_realmlist(data)
        manage_voices(data, voices_fr, log)   # voix gerables seulement en jeu FR
    build_patchz(data, base_fr, spells_fr, other_fr, log)
    deploy_addon(install_dir, log)         # corrige les interfaces custom en jeu FR
    set_locale(install_dir, "frFR" if base_fr else "enUS")
    log("Jeu=%s  Voix=%s  Sorts=%s  Reput=%s." %
        ("FR" if base_fr else "EN", "FR" if voices_fr else "EN",
         "FR" if spells_fr else "EN", "FR" if other_fr else "EN"))

# ------------------------------------------------------------------ interface
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EbonholdFR - Langue")
        self.geometry("640x600"); self.resizable(False, False)

        tk.Label(self, text="Ebonhold - Configurateur de langue",
                 font=("Segoe UI", 15, "bold")).pack(pady=(12, 0))
        tk.Label(self, text="Choisis ton dossier, regle chaque categorie, applique.",
                 font=("Segoe UI", 9)).pack(pady=(0, 6))

        frm = tk.Frame(self); frm.pack(fill="x", padx=16)
        self.path_var = tk.StringVar(value=find_ebonhold())
        tk.Entry(frm, textvariable=self.path_var).pack(side="left", fill="x", expand=True, ipady=3)
        tk.Button(frm, text="Parcourir...", command=self.browse).pack(side="left", padx=(6, 0))

        box = tk.LabelFrame(self, text=" Reglages ", font=("Segoe UI", 10, "bold"))
        box.pack(fill="x", padx=16, pady=8)
        self.base = tk.StringVar(value="FR")
        self.voices = tk.StringVar(value="FR")
        self.spells = tk.StringVar(value="FR")
        self.other = tk.StringVar(value="FR")
        self._row(box, "Jeu (interface, menus, quetes) :", self.base, "FR = pack frFR requis")
        self._row(box, "Voix :", self.voices, "(seulement si Jeu = FR)")
        self._row(box, "Sorts, talents & echoes :", self.spells, "")
        self._row(box, "Reputations, hauts faits & titres :", self.other, "")

        qf = tk.Frame(self); qf.pack(pady=(2, 0))
        tk.Button(qf, text="Tout en francais", command=lambda: self.set_all("FR")).pack(side="left", padx=4)
        tk.Button(qf, text="Tout en anglais", command=lambda: self.set_all("EN")).pack(side="left", padx=4)

        self.btn = tk.Button(self, text="  Appliquer  ", font=("Segoe UI", 12, "bold"),
                             bg="#2e7d32", fg="white", activebackground="#1b5e20",
                             activeforeground="white", command=self.run)
        self.btn.pack(pady=6, ipady=5)

        self.log = scrolledtext.ScrolledText(self, height=13, font=("Consolas", 9),
                                             state="disabled", bg="#1e1e1e", fg="#d4d4d4")
        self.log.pack(fill="both", expand=True, padx=16, pady=8)
        self._log("Pret. Le jeu doit etre FERME pendant l'operation.")

    def _row(self, parent, label, var, hint):
        f = tk.Frame(parent); f.pack(fill="x", padx=10, pady=4)
        tk.Label(f, text=label, font=("Segoe UI", 10), width=30, anchor="w").pack(side="left")
        tk.OptionMenu(f, var, "FR", "EN").pack(side="left")
        if hint:
            tk.Label(f, text=hint, font=("Segoe UI", 8), fg="#888").pack(side="left", padx=6)

    def set_all(self, v):
        self.base.set(v); self.voices.set(v); self.spells.set(v); self.other.set(v)

    def _log(self, m):
        self.log.configure(state="normal"); self.log.insert("end", m + "\n")
        self.log.see("end"); self.log.configure(state="disabled"); self.update_idletasks()

    def browse(self):
        d = filedialog.askdirectory(title="Dossier Ebonhold")
        if d: self.path_var.set(d)

    def run(self):
        install = self.path_var.get().strip()
        data = os.path.join(install, "Data")
        if not os.path.exists(os.path.join(data, "patch-5.MPQ")):
            messagebox.showerror("Dossier invalide",
                "Choisis le dossier Ebonhold (celui avec Wow.exe et le dossier Data).")
            return
        base_fr = (self.base.get() == "FR")
        if base_fr and not has_pack(data):
            if messagebox.askyesno("Pack frFR manquant",
                "Mettre le jeu (interface/menus/quetes) en francais necessite le pack frFR (~2,4 Go).\n\n"
                "Ouvrir la page de telechargement ?\n"
                "(Decompresse, place le dossier 'frFR' dans Data, puis relance.)"):
                webbrowser.open(PACK_URL)
            return
        self.btn.configure(state="disabled")
        def worker():
            try:
                apply_config(install, base_fr, self.voices.get() == "FR",
                             self.spells.get() == "FR", self.other.get() == "FR", self._log)
                self._log("\nTERMINE ! Lance Wow.exe depuis ce dossier.")
                messagebox.showinfo("Termine", "C'est fait ! Lance le jeu.")
            except Exception as e:
                self._log("\nERREUR : %s" % e)
                messagebox.showerror("Erreur", "Erreur : %s\n\nVerifie que le jeu est FERME." % e)
            finally:
                self.btn.configure(state="normal")
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
