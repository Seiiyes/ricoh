@echo off
echo.
echo ========================================
echo Ver Lecturas Disponibles
echo ========================================
echo.

if "%1"=="" (
    echo Mostrando todas las impresoras...
    docker exec -it ricoh-backend python ver_lecturas_disponibles.py
) else (
    echo Mostrando impresora %1...
    docker exec -it ricoh-backend python ver_lecturas_disponibles.py %1
)

echo.
pause
