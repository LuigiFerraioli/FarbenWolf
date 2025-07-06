@echo off

REM Stelle sicher, dass Python 3.11 installiert ist
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Bitte installiere Python 3.11 manuell.
    pause
    exit /b 1
)

REM Installiere Abhängigkeiten
pip install -r requirements.txt

REM Erstelle die exe
pyinstaller main.spec

echo ✅ Build complete.
pause