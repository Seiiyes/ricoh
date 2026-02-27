@echo off
echo ========================================
echo Aplicando Migración 004
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Ejecutar migración
python apply_migration_004.py

echo.
pause
