@echo off
title Publication Automatique WireFrame (GitHub)
cd /d "%~dp0"

echo ==============================================================
echo   ❖ PUBLICATION AUTOMATIQUE WIREFRAME (GitHub) ❖
echo ==============================================================
echo.

python ".git\hooks\auto_bump_version.py"
git add -A
git commit --no-verify -m "release: automatic WireFrame update"
git push origin main

echo.
echo ==============================================================
echo   ✅ Mise a jour publiee sur GitHub (Version auto-incrementee) !
echo ==============================================================
timeout /t 4
exit

