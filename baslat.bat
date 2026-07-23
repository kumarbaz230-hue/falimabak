@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo.
echo ========================================
echo   FalımaBak - Terminal Modu
echo   Eksik resim uyarilari asagida gorunur
echo ========================================
echo.

py -3.11 -u main.py

echo.
echo Uygulama kapandi. Yukaridaki ciktiyi kontrol et.
pause
