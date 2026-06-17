@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py enable_touchscreen.py
    exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
    python enable_touchscreen.py
    exit /b %errorlevel%
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/
echo Make sure to check "Add python.exe to PATH" during installation.
pause
exit /b 1
