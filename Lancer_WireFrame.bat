@echo off
chcp 65001 >nul
title Lancement de WireFrame (par Nyxo_17)
cd /d "%~dp0"

echo ========================================================
echo    ❖ WIREFRAME — COMPAGNON WARFRAME (par Nyxo_17) ❖
echo ========================================================

REM 1. Si l'executeur Python portable integre (runtime\) est present : AUCUNE installation requise !
if exist "%~dp0runtime\pythonw.exe" (
    set "TCL_LIBRARY=%~dp0runtime\tcl\tcl8.6"
    set "TK_LIBRARY=%~dp0runtime\tcl\tk8.6"
    set "PYTHONNOUSERSITE=1"
    echo Creation du raccourci WireFrame sur le Bureau Windows...
    powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\WireFrame.lnk'); $s.TargetPath='%~dp0runtime\pythonw.exe'; $s.Arguments='\"%~dp0main.py\"'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0data\app_icon.ico'; $s.Save()"
    echo Lancement immediat de WireFrame (Python integre)...
    start "" "%~dp0runtime\pythonw.exe" "%~dp0main.py"
    exit
)

REM 2. Sinon (clone depuis GitHub), verifie ou installe Python automatiquement
if not exist ".venv\Scripts\python.exe" (
    where python >nul 2>nul
    if errorlevel 1 (
        echo Installation automatique de Python en cours...
        curl.exe -sL -o "%TEMP%\py_setup.exe" "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
        "%TEMP%\py_setup.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_doc=0
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python310;%LOCALAPPDATA%\Programs\Python\Python310\Scripts;%PATH%"
    )
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
