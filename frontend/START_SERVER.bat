@echo off
echo Starting Vite Development Server...
echo.
echo Current directory: %CD%
echo.
echo If you see errors about index.html, please share them.
echo.
cd /d "%~dp0"
npm run dev
pause

