@echo off
setlocal

REM -------------------------------
REM Standard-Konfiguration
REM -------------------------------
set ONEDIR=0  REM Default: Onefile

REM -------------------------------
REM Argument prüfen
REM -------------------------------
if /i "%1%"=="onedir" set ONEDIR=1
if /i "%1%"=="onefile" set ONEDIR=0

REM -------------------------------
REM Prüfe, ob Python installiert ist
REM -------------------------------
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Bitte installiere Python 3.11 manuell.
    pause
    exit /b 1
)

REM -------------------------------
REM Abhängigkeiten installieren
REM -------------------------------
echo Installing dependencies...
pip install -r requirements.txt

REM -------------------------------
REM Build
REM -------------------------------
if "%ONEDIR%"=="1" (
    echo -------------------------------
    echo ONEDIR Build - SRC File
    echo -------------------------------
    pyinstaller --clean --onedir --name FarbenWolf src/main.py --noconsole
    REM Erstelle _internal Ordner, falls nicht existiert
    if not exist dist\FarbenWolf\_internal mkdir dist\FarbenWolf\_internal
    REM Kopiere den gesamten "resources"-Ordner hinein
    xcopy /s /e /i /y resources dist\FarbenWolf\_internal\resources >nul

) else (
    echo -------------------------------
    echo ONEFILE Build - SPEC File
    echo -------------------------------
    pyinstaller --clean FarbenWolf.spec
)

REM -------------------------------
REM Aufräumen
REM -------------------------------
rmdir /s /q build

echo Build complete.
pause
endlocal
