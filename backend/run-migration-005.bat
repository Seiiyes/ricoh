@echo off
REM Aplicar migración 005: Tablas de contadores
echo ================================================================================
echo APLICANDO MIGRACION 005: Tablas de Contadores
echo ================================================================================
echo.

cd /d "%~dp0"

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Ejecutar script de migración
python apply_migration_005.py

echo.
echo ================================================================================
echo Presiona cualquier tecla para salir...
pause >nul
