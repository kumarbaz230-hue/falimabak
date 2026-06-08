@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo Assetler olusturuluyor (1080p kalite)...
py -3 generate_all_assets.py
pause
