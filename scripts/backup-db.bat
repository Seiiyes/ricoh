@echo off
echo ========================================
echo   RESPALDO DE BASE DE DATOS
echo ========================================
echo.

REM Crear carpeta de respaldos si no existe
if not exist "backups" mkdir backups

REM Generar nombre con fecha y hora
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=backups\ricoh_backup_%TIMESTAMP%.sql

echo Creando respaldo en: %BACKUP_FILE%
echo.

REM Exportar base de datos
docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   RESPALDO CREADO EXITOSAMENTE
    echo ========================================
    echo.
    echo   Archivo: %BACKUP_FILE%
    echo.
    echo   Tamaño del archivo:
    for %%A in ("%BACKUP_FILE%") do echo   %%~zA bytes
    echo.
    echo   Ubicacion: %cd%\%BACKUP_FILE%
    echo.
    echo ========================================
    echo.
    echo IMPORTANTE:
    echo - Sube este archivo a GitHub o tu nube
    echo - Guardalo en un lugar seguro
    echo - Puedes restaurarlo con restore-db.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR AL CREAR RESPALDO
    echo ========================================
    echo.
    echo Verifica que Docker este corriendo:
    echo   docker ps
    echo.
)

echo ========================================
pause
