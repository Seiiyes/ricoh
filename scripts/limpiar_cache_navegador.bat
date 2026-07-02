@echo off
echo ========================================
echo   LIMPIAR CACHE DEL NAVEGADOR
echo   Sistema Ricoh - Frontend Responsive
echo ========================================
echo.
echo Los cambios de responsive YA ESTAN en el codigo.
echo El problema es que tu navegador tiene los estilos antiguos en cache.
echo.
echo ========================================
echo   INSTRUCCIONES:
echo ========================================
echo.
echo 1. Abre tu navegador en:
echo    http://192.168.91.34:5173
echo.
echo 2. Presiona una de estas combinaciones:
echo.
echo    Chrome/Edge:  Ctrl + Shift + R
echo    Firefox:      Ctrl + F5
echo.
echo 3. Los cambios se veran inmediatamente!
echo.
echo ========================================
echo   SI AUN NO SE VE:
echo ========================================
echo.
echo Opcion 1: Limpiar cache completo
echo    - Presiona: Ctrl + Shift + Delete
echo    - Selecciona: "Imagenes y archivos en cache"
echo    - Haz clic en: "Borrar datos"
echo    - Recarga con: F5
echo.
echo Opcion 2: Reiniciar el frontend
echo    - Ejecuta: docker-compose restart frontend
echo    - Espera 10 segundos
echo    - Limpia cache: Ctrl + Shift + R
echo.
echo Opcion 3: Modo incognito
echo    - Presiona: Ctrl + Shift + N
echo    - Ve a: http://192.168.91.34:5173
echo.
echo ========================================
echo   QUE VAS A VER:
echo ========================================
echo.
echo - Sidebar mas estrecho (256px en lugar de 320px)
echo - Mas espacio horizontal (+96px de espacio util)
echo - Texto mas compacto (titulos, labels, botones)
echo - Mejor densidad de informacion
echo - Grids optimizados (3-4 columnas en laptop)
echo.
echo ========================================
echo.
pause
