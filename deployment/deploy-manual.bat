@echo off
REM =============================================================================
REM DEPLOY MANUAL - Ricoh App a Servidor 192.168.91.131
REM Ejecutar este script desde: c:\Users\juan.lizarazo\Desktop\ricoh
REM =============================================================================

SET SERVER=192.168.91.131
SET USER=odootic
SET REMOTE_DIR=/home/odootic/ricoh-app

echo.
echo ============================================================
echo   Ricoh Equipment Management - Deploy a %SERVER%
echo ============================================================
echo.
echo   Necesitaras ingresar la contrasena de tu servidor varias veces.
echo.

REM Crear estructura de directorios en el servidor
echo [1/5] Creando directorio remoto...
ssh -o StrictHostKeyChecking=no %USER%@%SERVER% "mkdir -p %REMOTE_DIR%/backend %REMOTE_DIR%/src %REMOTE_DIR%/public %REMOTE_DIR%/deployment"

REM Copiar archivos del backend
echo [2/5] Copiando backend...
scp -o StrictHostKeyChecking=no -r backend\* %USER%@%SERVER%:%REMOTE_DIR%/backend/

REM Copiar frontend
echo [3/5] Copiando frontend (src, public)...
scp -o StrictHostKeyChecking=no -r src\* %USER%@%SERVER%:%REMOTE_DIR%/src/
scp -o StrictHostKeyChecking=no -r public\* %USER%@%SERVER%:%REMOTE_DIR%/public/ 2>nul
scp -o StrictHostKeyChecking=no package.json vite.config.ts tsconfig.json tsconfig.app.json index.html %USER%@%SERVER%:%REMOTE_DIR%/

REM Copiar docker-compose específico del servidor
echo [4/5] Copiando configuracion Docker...
scp -o StrictHostKeyChecking=no deployment\docker-compose.server131.yml %USER%@%SERVER%:%REMOTE_DIR%/docker-compose.yml
scp -o StrictHostKeyChecking=no deployment\install-server131.sh %USER%@%SERVER%:%REMOTE_DIR%/install.sh

REM Ejecutar instalacion en el servidor
echo [5/5] Ejecutando despliegue en el servidor...
ssh -o StrictHostKeyChecking=no %USER%@%SERVER% "chmod +x %REMOTE_DIR%/install.sh && cd %REMOTE_DIR% && sudo docker compose up --build -d"

echo.
echo ============================================================
echo   Verificando estado del despliegue...
echo ============================================================
ssh -o StrictHostKeyChecking=no %USER%@%SERVER% "cd %REMOTE_DIR% && sudo docker compose ps"

echo.
echo ============================================================
echo   ACCESO A LA APLICACION:
echo   Frontend:  http://%SERVER%
echo   Backend:   http://%SERVER%:8000
echo   API Docs:  http://%SERVER%:8000/docs
echo ============================================================
pause
