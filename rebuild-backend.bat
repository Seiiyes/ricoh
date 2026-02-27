@echo off
echo ========================================
echo Reconstruyendo Backend con Selenium
echo ========================================
echo.

echo [1/4] Deteniendo contenedores...
docker-compose down

echo.
echo [2/4] Reconstruyendo imagen del backend...
docker-compose build backend

echo.
echo [3/4] Iniciando contenedores...
docker-compose up -d

echo.
echo [4/4] Verificando estado...
timeout /t 5 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo Reconstruccion completada
echo ========================================
echo.
echo Para ver los logs del backend:
echo   docker logs ricoh-backend -f
echo.
pause
