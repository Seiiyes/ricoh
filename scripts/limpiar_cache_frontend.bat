@echo off
echo ========================================
echo Limpiando cache del frontend
echo ========================================

echo.
echo 1. Deteniendo contenedor frontend...
docker-compose stop frontend

echo.
echo 2. Eliminando contenedor frontend...
docker-compose rm -f frontend

echo.
echo 3. Limpiando cache de Vite dentro del contenedor...
docker-compose run --rm frontend sh -c "rm -rf node_modules/.vite"

echo.
echo 4. Reconstruyendo e iniciando frontend...
docker-compose up -d --build frontend

echo.
echo 5. Esperando que el frontend inicie...
timeout /t 10 /nobreak

echo.
echo 6. Mostrando logs del frontend...
docker logs ricoh-frontend --tail 20

echo.
echo ========================================
echo COMPLETADO
echo ========================================
echo.
echo IMPORTANTE: Ahora debes limpiar el cache del navegador:
echo.
echo Chrome/Edge:
echo   1. Presiona Ctrl + Shift + Delete
echo   2. Selecciona "Imagenes y archivos en cache"
echo   3. Haz clic en "Borrar datos"
echo   4. O simplemente presiona Ctrl + F5 en la pagina
echo.
echo Firefox:
echo   1. Presiona Ctrl + Shift + Delete
echo   2. Selecciona "Cache"
echo   3. Haz clic en "Limpiar ahora"
echo   4. O simplemente presiona Ctrl + F5 en la pagina
echo.
echo Luego abre: http://192.168.91.34:5173
echo ========================================

pause
