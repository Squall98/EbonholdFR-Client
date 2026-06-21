# -*- coding: utf-8 -*-
"""EbonholdFR - Configurateur de langue (interface graphique).

Methode NON-DESTRUCTIVE : le francais est injecte dans un patch SEPARE 'patch-Z.MPQ'
qui surcharge patch-5/6 SANS les modifier (compatible launcher, survit aux MAJ serveur).

Profils :
  - Tout en francais        : pack frFR + patch-Z(colonne frFR) + langue frFR
  - Jeu anglais + contenu FR : patch-Z(colonne enUS) + langue enUS (PAS besoin du pack)
  - Anglais (desactiver)     : retire patch-Z + langue enUS

Compilable en .exe (build_exe.bat) : aucun Python requis cote utilisateur.
"""
import os, sys, json, threading, shutil, webbrowser
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

# ------------------------------------------------------------------ logique
def load_tr():
    s = json.load(open(STORE_PATH, encoding="utf-8"))
    tr = {}
    tr.update(s.get("names", {}))
    tr.update(s.get("descs", {}))
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
    lines = []
    if os.path.exists(cfg):
        lines = open(cfg, encoding="latin-1").read().splitlines()
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
    """Aligne le realmlist du pack frFR sur celui du client (Ebonhold)."""
    en = os.path.join(data_dir, "enUS", "realmlist.wtf")
    fr = os.path.join(data_dir, "frFR", "realmlist.wtf")
    if os.path.exists(en) and os.path.isdir(os.path.dirname(fr)):
        shutil.copy2(en, fr)

def build_patchz(data_dir, fr_col, log):
    """Construit patch-Z.MPQ (FR injecte) sans toucher patch-5/6."""
    tr = load_tr()
    log("Traductions : %d" % len(tr))
    fr_arch = []
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
            raw = a.read_file(n)
            base = find_base(n)
            try:
                merged, st = dbc_localize.merge(raw, base, tr, fr_col=fr_col)
            except Exception:
                merged = None
            if merged:
                patchz[n] = merged
    out = os.path.join(data_dir, "patch-Z.MPQ")
    mpqwrite.create_mpq(out, patchz)
    log("patch-Z.MPQ ecrit (%d DBC)." % len(patchz))

def remove_patchz(data_dir):
    p = os.path.join(data_dir, "patch-Z.MPQ")
    if os.path.exists(p):
        os.remove(p)

# Profils -> action
def apply_profile(install_dir, profile, log):
    data = os.path.join(install_dir, "Data")
    if profile == "full":
        fix_realmlist(data)
        build_patchz(data, fr_col=2, log=log)   # FR dans la colonne frFR
        set_locale(install_dir, "frFR")
        log("Profil : TOUT EN FRANCAIS applique.")
    elif profile == "content":
        build_patchz(data, fr_col=0, log=log)    # FR dans la colonne enUS
        set_locale(install_dir, "enUS")
        log("Profil : JEU ANGLAIS + CONTENU FRANCAIS applique.")
    elif profile == "english":
        remove_patchz(data)
        set_locale(install_dir, "enUS")
        log("Profil : ANGLAIS (francais desactive).")

# ------------------------------------------------------------------ interface
class App(tk.Tk):
    PROFILES = [
        ("full",    "Tout en francais  (recommande - necessite le pack frFR)"),
        ("content", "Jeu en anglais + sorts/echoes en francais  (sans pack)"),
        ("english", "Anglais  (desactiver le francais)"),
    ]

    def __init__(self):
        super().__init__()
        self.title("EbonholdFR - Configurateur de langue")
        self.geometry("660x560"); self.resizable(False, False)

        tk.Label(self, text="Ebonhold - Langue", font=("Segoe UI", 16, "bold")).pack(pady=(14, 0))
        tk.Label(self, text="Choisis ton dossier Ebonhold, un profil, puis applique.",
                 font=("Segoe UI", 9)).pack(pady=(0, 8))

        frm = tk.Frame(self); frm.pack(fill="x", padx=16)
        self.path_var = tk.StringVar(value=find_ebonhold())
        tk.Entry(frm, textvariable=self.path_var).pack(side="left", fill="x", expand=True, ipady=3)
        tk.Button(frm, text="Parcourir...", command=self.browse).pack(side="left", padx=(6, 0))

        box = tk.LabelFrame(self, text=" Profil de langue ", font=("Segoe UI", 10, "bold"))
        box.pack(fill="x", padx=16, pady=10)
        self.profile = tk.StringVar(value="full")
        for val, label in self.PROFILES:
            tk.Radiobutton(box, text=label, variable=self.profile, value=val,
                           font=("Segoe UI", 10), anchor="w").pack(fill="x", padx=8, pady=2)

        self.btn = tk.Button(self, text="  Appliquer  ", font=("Segoe UI", 12, "bold"),
                             bg="#2e7d32", fg="white", activebackground="#1b5e20",
                             activeforeground="white", command=self.run)
        self.btn.pack(pady=4, ipady=6)

        self.log = scrolledtext.ScrolledText(self, height=15, font=("Consolas", 9),
                                             state="disabled", bg="#1e1e1e", fg="#d4d4d4")
        self.log.pack(fill="both", expand=True, padx=16, pady=10)
        self._log("Pret. Le jeu doit etre FERME pendant l'operation.")

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
                "Choisis le dossier Ebonhold (celui qui contient Wow.exe et le dossier Data).")
            return
        prof = self.profile.get()
        if prof == "full" and not has_pack(data):
            if messagebox.askyesno("Pack frFR manquant",
                "Le profil 'Tout en francais' a besoin du pack de langue frFR (~2,4 Go),\n"
                "qui n'est pas installe.\n\n"
                "Veux-tu ouvrir la page de telechargement ?\n"
                "(Decompresse l'archive et place le dossier 'frFR' dans le dossier Data,\n"
                " puis relance ce configurateur.)"):
                webbrowser.open(PACK_URL)
            return
        self.btn.configure(state="disabled")
        def worker():
            try:
                apply_profile(install, prof, self._log)
                self._log("\nTERMINE ! Lance Wow.exe depuis ce dossier.")
                messagebox.showinfo("Termine", "C'est fait ! Lance le jeu pour voir le resultat.")
            except Exception as e:
                self._log("\nERREUR : %s" % e)
                messagebox.showerror("Erreur",
                    "Erreur : %s\n\nVerifie que le jeu est bien FERME, puis reessaie." % e)
            finally:
                self.btn.configure(state="normal")
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
