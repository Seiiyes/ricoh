@echo off
echo ========================================
echo Iniciando Servidor Backend
echo ========================================
echo.
echo IMPORTANTE: Deja esta ventana abierta
echo.
echo Para detener el servidor: Ctrl+C
echo ========================================
echo.

cd /d "%~dp0"
python -m uvicorn main:app --reload

pause
