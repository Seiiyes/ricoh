@echo off
REM Script para aplicar migración 003 con entorno virtual

echo ========================================
echo Aplicando Migración 003
echo ========================================
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Aplicar migración
python apply_migration_003_sqlalchemy.py

REM Mantener ventana abierta
echo.
echo Presiona cualquier tecla para cerrar...
pause > nul
