# -*- coding: utf-8 -*-
"""EbonholdFR - Installeur (interface graphique).
L'utilisateur choisit son dossier Ebonhold et clique sur un bouton : la traduction
francaise est injectee dans les .dbc et la langue passe en frFR. Reversible.

Compilable en .exe (voir build_exe.bat) : aucun Python requis cote utilisateur.
"""
import os, sys, json, threading, shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ------------------------------------------------------------------ ressources
def resource(rel):
    """Chemin d'une ressource embarquee (marche en dev ET compile PyInstaller)."""
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, rel)
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", rel))

sys.path.insert(0, resource("tools"))
import mpqwrite, dbc_localize  # noqa: E402

STORE_PATH = resource("data/custom_translations.json")
FR_MPQS = ["patch-frFR-3.MPQ", "patch-frFR-2.MPQ", "patch-frFR.MPQ", "locale-frFR.MPQ"]
TEXT_PATCHES = ["patch-5.MPQ", "patch-6.MPQ"]
DOWNLOAD_URL = "https://forum.warmane.com/showthread.php?t=388077"  # pack frFR (dossier frFR)

# ------------------------------------------------------------------ logique
def load_tr():
    s = json.load(open(STORE_PATH, encoding="utf-8"))
    tr = {}
    tr.update(s.get("names", {}))
    tr.update(s.get("descs", {}))
    return tr

def find_ebonhold():
    """Cherche une install Ebonhold (dossier contenant Data\\patch-5.MPQ)."""
    cands = []
    for drive in "CDEFGH":
        for sub in (r"\ebonhold\Ebonhold", r"\ebonhold-FR", r"\Ebonhold",
                    r"\Games\Ebonhold", r"\Program Files\Ebonhold",
                    r"\Program Files (x86)\Ebonhold"):
            cands.append(drive + ":" + sub)
    for c in cands:
        if os.path.exists(os.path.join(c, "Data", "patch-5.MPQ")):
            return c
    return ""

def has_frfr(data_dir):
    return os.path.exists(os.path.join(data_dir, "frFR", "locale-frFR.MPQ"))

def import_mpq(p):
    import mpyq
    return mpyq.MPQArchive(p)

def set_locale(install_dir, locale):
    cfg = os.path.join(install_dir, "WTF", "Config.wtf")
    if not os.path.exists(cfg):
        return False
    lines = open(cfg, encoding="latin-1").read().splitlines()
    out, found = [], False
    for ln in lines:
        if ln.strip().upper().startswith("SET LOCALE"):
            out.append('SET locale "%s"' % locale); found = True
        else:
            out.append(ln)
    if not found:
        out.insert(0, 'SET locale "%s"' % locale)
    open(cfg, "w", encoding="latin-1").write("\n".join(out) + "\n")
    return True

def apply_fr(install_dir, log):
    import mpyq
    data_dir = os.path.join(install_dir, "Data")
    tr = load_tr()
    log("Traductions chargees : %d" % len(tr))

    fr_arch = []
    for m in FR_MPQS:
        fp = os.path.join(data_dir, "frFR", m)
        if os.path.exists(fp):
            try: fr_arch.append(mpyq.MPQArchive(fp, listfile=False))
            except Exception: pass

    def find_base(path):
        for a in fr_arch:
            try:
                d = a.read_file(path)
                if d: return d
            except Exception: pass
        return None

    for patch in TEXT_PATCHES:
        dp = os.path.join(data_dir, patch)
        if not os.path.exists(dp):
            log("  (%s introuvable, ignore)" % patch); continue
        bak = dp + ".bak"
        if not os.path.exists(bak):
            shutil.copy2(dp, bak); log("  sauvegarde %s.bak creee" % patch)
        src = bak  # on lit toujours la version d'origine (anglaise) comme source
        a = mpyq.MPQArchive(src)
        names = [n for n in a.read_file("(listfile)").decode("latin-1")
                 .replace("\r\n", "\n").split("\n") if n.strip()]
        out = {}
        for n in names:
            raw = a.read_file(n)
            if not n.lower().endswith(".dbc"):
                out[n] = raw; continue
            base = find_base(n)
            try:
                merged, st = dbc_localize.merge(raw, base, tr)
            except Exception:
                merged = None
            out[n] = merged if merged else raw
        mpqwrite.create_mpq(dp, out)
        log("  %s traduit." % patch)

    set_locale(install_dir, "frFR")
    log("Langue du jeu : francais (frFR).")

def restore_en(install_dir, log):
    data_dir = os.path.join(install_dir, "Data")
    for patch in TEXT_PATCHES:
        dp = os.path.join(data_dir, patch)
        bak = dp + ".bak"
        if os.path.exists(bak):
            shutil.copy2(bak, dp); log("  %s restaure (anglais)." % patch)
    set_locale(install_dir, "enUS")
    log("Langue du jeu : anglais (enUS).")

# ------------------------------------------------------------------ interface
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EbonholdFR - Traduction francaise")
        self.geometry("640x520")
        self.resizable(False, False)

        tk.Label(self, text="Ebonhold en francais", font=("Segoe UI", 16, "bold")).pack(pady=(14, 2))
        tk.Label(self, text="Choisis ton dossier Ebonhold, puis clique sur le bouton.",
                 font=("Segoe UI", 9)).pack()

        frm = tk.Frame(self); frm.pack(fill="x", padx=16, pady=10)
        self.path_var = tk.StringVar(value=find_ebonhold())
        tk.Entry(frm, textvariable=self.path_var).pack(side="left", fill="x", expand=True, ipady=3)
        tk.Button(frm, text="Parcourir...", command=self.browse).pack(side="left", padx=(6, 0))

        self.btn = tk.Button(self, text="  Mettre Ebonhold en francais  ",
                             font=("Segoe UI", 12, "bold"), bg="#2e7d32", fg="white",
                             activebackground="#1b5e20", activeforeground="white",
                             command=lambda: self.run(apply_fr))
        self.btn.pack(pady=(4, 4), ipady=6)
        self.btn_restore = tk.Button(self, text="Restaurer l'anglais",
                                     command=lambda: self.run(restore_en))
        self.btn_restore.pack()

        self.log = scrolledtext.ScrolledText(self, height=16, font=("Consolas", 9),
                                             state="disabled", bg="#1e1e1e", fg="#d4d4d4")
        self.log.pack(fill="both", expand=True, padx=16, pady=12)
        self._log("Pret. Selectionne ton dossier Ebonhold (celui qui contient Wow.exe).")

    def _log(self, msg):
        self.log.configure(state="normal")
        self.log.insert("end", msg + "\n"); self.log.see("end")
        self.log.configure(state="disabled"); self.update_idletasks()

    def browse(self):
        d = filedialog.askdirectory(title="Selectionne ton dossier Ebonhold")
        if d: self.path_var.set(d)

    def run(self, func):
        install = self.path_var.get().strip()
        if not os.path.exists(os.path.join(install, "Data", "patch-5.MPQ")):
            messagebox.showerror("Dossier invalide",
                "Ce dossier n'est pas une installation Ebonhold.\n"
                "Choisis le dossier qui contient Wow.exe et le dossier Data.")
            return
        if func is apply_fr and not has_frfr(os.path.join(install, "Data")):
            if not messagebox.askyesno("Pack francais manquant",
                "Les fichiers de langue francaise (frFR) ne sont pas installes.\n\n"
                "Le jeu de base restera en anglais (seul le contenu custom sera traduit).\n"
                "Pour un jeu 100%% francais, installe d'abord le pack frFR :\n%s\n\n"
                "Continuer quand meme ?" % DOWNLOAD_URL):
                return
        self.btn.configure(state="disabled"); self.btn_restore.configure(state="disabled")
        def worker():
            try:
                func(install, self._log)
                self._log("\nTERMINE ! Lance le jeu depuis ce dossier.")
                messagebox.showinfo("Termine", "C'est fait ! Lance Wow.exe depuis ce dossier.")
            except Exception as e:
                self._log("\nERREUR : %s" % e)
                messagebox.showerror("Erreur",
                    "Une erreur est survenue :\n%s\n\n"
                    "Verifie que le jeu est bien FERME, puis reessaie." % e)
            finally:
                self.btn.configure(state="normal"); self.btn_restore.configure(state="normal")
        threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    App().mainloop()
