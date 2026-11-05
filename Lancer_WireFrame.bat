@echo off
chcp 65001 >nul
title Installation et Lancement de WireFrame (par Nyxo_17)
cd /d "%~dp0"

echo ========================================================
echo    ❖ WIREFRAME — COMPAGNON WARFRAME (par Nyxo_17) ❖
echo ========================================================

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creation de l'environnement Python local...
    python -m venv .venv
    echo [2/3] Installation des bibliotheques requises...
    .venv\Scripts\pip.exe install -r requirements.txt
    echo [3/3] Creation du raccourci WireFrame sur le Bureau...
    powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\WireFrame.lnk'); $s.TargetPath='%~dp0.venv\Scripts\pythonw.exe'; $s.Arguments='\"%~dp0main.py\"'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0data\app_icon.ico'; $s.Save()"
)

echo Lancement de WireFrame...
start "" ".venv\Scripts\pythonw.exe" "main.py"
exit
