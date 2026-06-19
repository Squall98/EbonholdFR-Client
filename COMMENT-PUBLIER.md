# 📤 Comment publier ce projet sur GitHub (guide pas-à-pas)

Pas besoin de t'y connaître. Suis les étapes dans l'ordre. ⏱️ ~10 minutes.

> ✅ Le dépôt est **déjà prêt** sur ton PC (git initialisé, fichiers ajoutés, 1er commit fait).
> Il ne reste qu'à l'envoyer sur GitHub. La méthode A (GitHub Desktop) est la plus simple.

---

## Étape 0 — Avoir un compte GitHub

1. Va sur **https://github.com**
2. Si tu n'as pas de compte : clique **Sign up** et crée-en un (gratuit).
   Si tu en as déjà un (ex. *Squall98*), connecte-toi.

---

## 🟢 Méthode A — GitHub Desktop (recommandée, sans commande)

### A.1 — Installer GitHub Desktop
1. Va sur **https://desktop.github.com**
2. Clique **Download for Windows**, installe, puis ouvre-le.
3. Connecte-toi avec ton compte GitHub (**File → Options → Accounts → Sign in**).

### A.2 — Ajouter le projet
1. Menu **File → Add local repository**.
2. Clique **Choose...** et sélectionne le dossier :
   ```
   V:\Project\Ebonhold\github\EbonholdFR-Client
   ```
3. Clique **Add repository**.

### A.3 — Publier
1. En haut, clique le bouton **Publish repository**.
2. Dans la fenêtre :
   - **Name** : `EbonholdFR-Client`
   - **Keep this code private** : ⬜ **DÉCOCHE** la case (pour que ce soit public).
3. Clique **Publish repository**.

🎉 C'est en ligne ! Adresse : `https://github.com/TON-PSEUDO/EbonholdFR-Client`

➡️ Passe ensuite à l'**Étape finale** (ajouter l'installeur .exe).

---

## ⚙️ Méthode B — En ligne de commande (alternative)

> À faire seulement si tu préfères les commandes. Git est déjà installé sur ton PC.

### B.1 — Créer un dépôt VIDE sur GitHub
1. Sur **https://github.com**, clique le **+** en haut à droite → **New repository**.
2. **Repository name** : `EbonholdFR-Client`
3. Coche **Public**.
4. ⚠️ **NE COCHE RIEN d'autre** (pas de README, pas de .gitignore, pas de licence).
5. Clique **Create repository**.

### B.2 — Envoyer le projet
1. Ouvre **Git Bash** (clic droit dans le dossier `EbonholdFR-Client` → *Open Git Bash here*).
2. Copie-colle ces 3 lignes (**remplace `TON-PSEUDO`** par ton pseudo GitHub) :
   ```bash
   git remote add origin https://github.com/TON-PSEUDO/EbonholdFR-Client.git
   git branch -M main
   git push -u origin main
   ```
3. Une fenêtre te demandera de te connecter à GitHub → fais-le.

🎉 C'est en ligne !

---

## 🏁 Étape finale — Ajouter l'installeur (.exe) en téléchargement

L'exe n'est volontairement pas dans le dépôt (trop lourd). On l'ajoute comme **Release**, pour que les joueurs le téléchargent en 1 clic.

1. **Compile l'exe** s'il n'existe pas encore : double-clique sur
   `installer\build_exe.bat` → il crée `installer\dist\EbonholdFR-Installer.exe`.
2. Sur la page de ton dépôt GitHub, clique **Releases** (à droite) → **Create a new release**.
3. **Choose a tag** : tape `v1.0` puis clique **Create new tag**.
4. **Release title** : `EbonholdFR-Client v1.0`
5. **Description** : par ex. *« Traduction française du client Project Ebonhold. Double-clique l'installeur, choisis ton dossier, c'est tout. »*
6. **Glisse-dépose** le fichier `EbonholdFR-Installer.exe` dans la zone *« Attach binaries »*.
7. Clique **Publish release**.

🎉 Les joueurs peuvent maintenant télécharger l'installeur depuis l'onglet **Releases** !

---

## ❓ Problèmes courants

- **« remote origin already exists »** (méthode B) → tape d'abord :
  `git remote remove origin` puis recommence.
- **Demande de mot de passe qui échoue** → GitHub n'accepte plus le mot de passe en ligne
  de commande ; utilise plutôt **GitHub Desktop** (méthode A), c'est plus simple.
- **Tu veux mettre à jour le projet plus tard** → modifie les fichiers, puis dans GitHub
  Desktop : écris un petit résumé en bas à gauche → **Commit to main** → **Push origin**.
