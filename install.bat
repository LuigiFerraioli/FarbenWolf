@echo off
setlocal

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

echo -------------------------------
echo ONEFILE Build - SPEC File
echo -------------------------------
pyinstaller --clean FarbenWolf.spec
xcopy /s /e /i /y resources dist\FarbenWolf\_internal\resources >nul

REM -------------------------------
REM Aufräumen
REM -------------------------------
rmdir /s /q build

echo Build complete.
pause
endlocal
