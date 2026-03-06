@echo off
REM ================================================================================
REM Script para iniciar el servidor API de Ricoh
REM ================================================================================

echo.
echo ================================================================================
echo 🚀 INICIANDO SERVIDOR API DE RICOH
echo ================================================================================
echo.

REM Activar entorno virtual y ejecutar servidor
call venv\Scripts\activate.bat
python main.py

pause
