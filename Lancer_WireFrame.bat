@echo off
title WireFrame HTML5 - 144 FPS (par Nyxo_17)
cd /d "%~dp0"

set "HTML_PATH=%~dp0index.html"
set "FILE_URL=file:///%HTML_PATH:\=/%"

set "EDGE_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE_EXE%" set "EDGE_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"

if exist "%EDGE_EXE%" (
    powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\WireFrame.lnk'); $s.TargetPath='%EDGE_EXE%'; $s.Arguments='--app=\"%FILE_URL%\" --window-size=1420,860'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0data\app_icon.ico'; $s.Save()" >nul 2>nul
    start "" "%EDGE_EXE%" --app="%FILE_URL%" --window-size=1420,860
    exit
)

start "" "%HTML_PATH%"
exit
