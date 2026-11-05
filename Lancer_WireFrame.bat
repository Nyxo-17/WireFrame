@echo off
title WireFrame HTML5 - 144 FPS (par Nyxo_17)
cd /d "%~dp0"

set "HTML_PATH=%~dp0index.html"
set "FILE_URL=file:///%HTML_PATH:\=/%"

REM Creation automatique du raccourci WireFrame sur le Bureau Windows avec l'icone officielle
if not exist "%USERPROFILE%\Desktop\WireFrame.lnk" (
    powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\WireFrame.lnk'); $s.TargetPath='%~dp0Lancer_WireFrame.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0data\app_icon.ico'; $s.WindowStyle=7; $s.Save()" >nul 2>nul
)

REM Ouvre WireFrame HTML5 en mode Application Desktop native (sans barre d'adresse) via Microsoft Edge
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app="%FILE_URL%" --window-size=1420,860
    exit
)
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" --app="%FILE_URL%" --window-size=1420,860
    exit
)

REM Secours : ouvre dans le navigateur par defaut
start "" "%HTML_PATH%"
exit
