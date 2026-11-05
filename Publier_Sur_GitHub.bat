@echo off
chcp 65001 >nul
title Publication de WireFrame sur GitHub (Nyxo-17)
cd /d "C:\Users\maxim\.gemini\antigravity\scratch\wireframe_v1"

echo ==============================================================
echo    🚀 ENVOI DE WIREFRAME VERS GITHUB (Nyxo-17/WireFrame)
echo ==============================================================
echo.
echo 1. Si une fenetre GitHub s'ouvre, clique sur "Sign in with your browser"
echo    (Se connecter avec le navigateur) puis sur "Authorize".
echo.

git branch -M main
git remote set-url origin https://github.com/Nyxo-17/WireFrame.git
git push -u origin main

echo.
echo ==============================================================
echo    ✅ TERMINE ! Actualise ta page GitHub :
echo    https://github.com/Nyxo-17/WireFrame
echo ==============================================================
pause
