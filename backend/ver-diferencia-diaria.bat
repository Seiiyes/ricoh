@echo off
echo ================================================================================
echo VER DIFERENCIA DE CONSUMO ENTRE DOS LECTURAS
echo ================================================================================
echo.
echo Este script te permite comparar dos lecturas de contadores para ver:
echo   - Cuantas paginas se imprimieron entre las dos lecturas
echo   - Consumo por funcion (copiadora, impresora, escaner)
echo   - Top 10 usuarios con mayor consumo
echo   - Validacion de integridad (suma usuarios vs total impresora)
echo.
echo Presione cualquier tecla para continuar...
pause > nul

docker exec -it ricoh-backend python ver_diferencia_diaria.py

echo.
echo ================================================================================
echo Comparacion finalizada
echo ================================================================================
pause
