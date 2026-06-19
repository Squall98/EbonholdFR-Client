@echo off
REM Compile l'installeur en un seul .exe autonome (aucun Python requis cote utilisateur).
REM Prerequis (machine de build uniquement) : pip install pyinstaller mpyq
cd /d "%~dp0"
pyinstaller --noconfirm --onefile --windowed --name "EbonholdFR-Installer" ^
  --paths "..\tools" ^
  --add-data "..\data\custom_translations.json;data" ^
  --add-data "..\tools\mpqwrite.py;tools" ^
  --add-data "..\tools\dbc_localize.py;tools" ^
  --hidden-import mpqwrite --hidden-import dbc_localize --hidden-import mpyq ^
  ebonhold_fr_installer.py
echo.
echo === Termine : installer\dist\EbonholdFR-Installer.exe ===
pause
