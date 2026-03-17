@echo off
echo ========================================
echo Iniciando Servidor Backend (con venv)
echo ========================================
echo.

cd /d "%~dp0"

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando servidor en 0.0.0.0:8000...
echo IMPORTANTE: Deja esta ventana abierta
echo Para detener: Ctrl+C
echo ========================================
echo.

python uvicorn_config.py

pause
