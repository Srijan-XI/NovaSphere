@echo off
setlocal EnableExtensions

rem NovaSphere web server launcher.
rem The Flask backend serves the frontend assets and exposes the API.
set "WEB_DIR=%~dp0"
for %%I in ("%WEB_DIR%..") do set "PROJECT_ROOT=%%~fI"
set "PYTHONPATH=%PROJECT_ROOT%\src;%PROJECT_ROOT%"
set "FRONTEND_DIR=%WEB_DIR%frontend"
set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8080"

echo.
echo NovaSphere web server
echo ====================

if not exist "%FRONTEND_DIR%\index.html" (
    echo ERROR: Frontend files are missing: "%FRONTEND_DIR%"
    exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found on PATH.
    echo Install Python 3.7 or newer and try again.
    exit /b 1
)

python -c "import sys; assert sys.version_info >= (3, 7), 'Python 3.7 or newer is required'" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.7 or newer is required.
    exit /b 1
)

echo Checking web requirements...
python -c "import flask, flask_cors, psutil, sqlite3" >nul 2>&1
if errorlevel 1 (
    echo Web requirements are missing. Installing from web\requirements.txt...
    python -m pip install -r "%WEB_DIR%requirements.txt"
    if errorlevel 1 (
        echo ERROR: Failed to install web requirements.
        exit /b 1
    )
)

echo Requirements OK.
echo Frontend: %FRONTEND_DIR%
echo Backend:  http://%BACKEND_HOST%:%BACKEND_PORT%
echo Press Ctrl+C to stop NovaSphere.
echo.

cd /d "%PROJECT_ROOT%"
python -m web.backend.app --host "%BACKEND_HOST%" --port %BACKEND_PORT%
set "EXIT_CODE=%ERRORLEVEL%"
cd /d "%PROJECT_ROOT%"
exit /b %EXIT_CODE%
