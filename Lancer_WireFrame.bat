@echo off
title WireFrame HTML5 - 144 FPS (par Nyxo_17)
cd /d "%~dp0"

if exist "%~dp0WireFrame.exe" (
    powershell -NoProfile -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\WireFrame.lnk'); $s.TargetPath='%~dp0WireFrame.exe'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0data\app_icon.ico'; $s.Save()" >nul 2>nul
    start "" "%~dp0WireFrame.exe"
    exit
)

start "" "%~dp0index.html"
exit
