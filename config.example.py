# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Renomme ce fichier en  config.py  puis adapte les chemins a ton installation.
# (config.py est ignore par git, tes chemins perso ne seront jamais publies.)
# ----------------------------------------------------------------------------

# Dossier "Data" du client Ebonhold ORIGINAL (anglais, tenu a jour par le launcher).
# C'est la SOURCE : on y lit les patchs custom du serveur (pristine).
SRC_DATA = r"C:\Games\Ebonhold\Data"

# Dossier "Data" de ta COPIE francaise du client (locale frFR installee).
# C'est la SORTIE : on y reecrit les patchs traduits. Ton install d'origine reste intacte.
DST_DATA = r"C:\Games\Ebonhold-FR\Data"

# (Optionnel) Chemin du fichier EbonholdFR_Data.lua de l'addon EbonholdFR.
# Sert uniquement a extract_custom_spells.py pour EXCLURE les echoes deja traduits
# par l'addon (tooltips). Laisse None si tu n'utilises pas l'addon.
ADDON_DATA = None
