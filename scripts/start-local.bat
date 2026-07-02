@echo off
echo ========================================
echo   Sistema Ricoh - Modo Local
echo ========================================
echo.
echo Este script iniciara:
echo   1. Base de datos (Docker)
echo   2. Frontend (Docker)
echo   3. Backend (Local - Python)
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

REM Detener contenedores anteriores
echo.
echo Deteniendo contenedores anteriores...
docker-compose down

REM Iniciar solo DB y Frontend
echo.
echo Iniciando base de datos y frontend...
docker-compose -f docker-compose-db-only.yml up -d

REM Esperar a que la DB este lista
echo.
echo Esperando a que la base de datos este lista...
timeout /t 5 /nobreak >nul

REM Iniciar backend local en una nueva ventana
echo.
echo Iniciando backend local...
start "Ricoh Backend" cmd /k start-backend-local.bat

echo.
echo ========================================
echo   Sistema iniciado correctamente
echo ========================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000
echo   Adminer:  http://localhost:8080
echo.
echo Presiona cualquier tecla para salir...
pause >nul
