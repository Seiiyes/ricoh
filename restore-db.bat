@echo off
echo ========================================
echo   RESTAURAR BASE DE DATOS
echo ========================================
echo.

REM Verificar que existe la carpeta de respaldos
if not exist "backups" (
    echo ✗ No existe la carpeta de respaldos
    echo   Crea un respaldo primero con backup-db.bat
    echo.
    pause
    exit /b
)

REM Listar respaldos disponibles
echo Respaldos disponibles:
echo.
dir /b backups\*.sql
echo.

set /p BACKUP_FILE="Ingresa el nombre del archivo a restaurar: "

if not exist "backups\%BACKUP_FILE%" (
    echo.
    echo ✗ Archivo no encontrado: backups\%BACKUP_FILE%
    echo.
    pause
    exit /b
)

echo.
echo ========================================
echo   ADVERTENCIA
echo ========================================
echo.
echo Esto SOBRESCRIBIRA la base de datos actual
echo Todos los datos actuales se PERDERAN
echo.
echo Archivo a restaurar: %BACKUP_FILE%
echo.
set /p CONFIRM="¿Estas seguro? (S/N): "

if /i not "%CONFIRM%"=="S" (
    echo.
    echo Operacion cancelada
    echo.
    pause
    exit /b
)

echo.
echo Restaurando base de datos...
echo Por favor espera...
echo.

REM Restaurar base de datos
docker exec -i ricoh-postgres psql -U ricoh_admin ricoh_fleet < backups\%BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   BASE DE DATOS RESTAURADA
    echo ========================================
    echo.
    echo ✓ La base de datos se restauro exitosamente
    echo.
    echo Reinicia el frontend para ver los cambios:
    echo   1. Abre http://localhost:5173
    echo   2. Recarga la pagina (F5)
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR AL RESTAURAR
    echo ========================================
    echo.
    echo Verifica que Docker este corriendo:
    echo   docker ps
    echo.
)

echo ========================================
pause
