@echo off
echo ================================================================================
echo PRUEBA DE CIERRE MENSUAL CON SNAPSHOT DE USUARIOS
echo ================================================================================
echo.
echo Este script prueba el cierre mensual con las siguientes validaciones:
echo   - Verificacion de impresora existente
echo   - Validacion de no duplicados
echo   - Validacion de fecha (no futuro, max 2 meses atras)
echo   - Validacion de contador reciente (max 7 dias)
echo   - Validacion de secuencia de cierres
echo   - Deteccion de reset de contador
echo   - Creacion de snapshot inmutable de usuarios
echo   - Validacion de integridad (suma usuarios vs total impresora)
echo   - Generacion de hash SHA256 de verificacion
echo.
echo Presione cualquier tecla para continuar...
pause > nul

docker exec -it ricoh-backend python test_cierre_mensual.py

echo.
echo ================================================================================
echo Prueba finalizada
echo ================================================================================
pause
