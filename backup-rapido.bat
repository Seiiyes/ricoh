@echo off
REM Script rapido para respaldo sin pausas
REM Util para automatizar o usar en scripts

if not exist "backups" mkdir backups

set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set BACKUP_FILE=backups\ricoh_backup_%TIMESTAMP%.sql

docker exec ricoh-postgres pg_dump -U ricoh_admin ricoh_fleet > %BACKUP_FILE%

if %ERRORLEVEL% EQU 0 (
    echo Respaldo creado: %BACKUP_FILE%
) else (
    echo Error al crear respaldo
)
