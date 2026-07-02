@echo off
echo ========================================
echo   INSTALANDO DEPENDENCIAS
echo ========================================
echo.
echo Este proceso puede tardar 2-3 minutos...
echo.

REM Instalar dependencias de Node.js
echo [1/2] Instalando dependencias de Node.js...
call npm install

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   INSTALACION COMPLETADA
    echo ========================================
    echo.
    echo Las dependencias se instalaron correctamente.
    echo.
    echo Ahora:
    echo 1. Reinicia tu editor (VS Code, etc.)
    echo 2. O presiona Ctrl+Shift+P y busca:
    echo    "TypeScript: Restart TS Server"
    echo.
    echo Las lineas rojas deberian desaparecer.
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR EN LA INSTALACION
    echo ========================================
    echo.
    echo Hubo un error al instalar las dependencias.
    echo.
    echo Intenta:
    echo 1. Cerrar todos los programas que usen Node.js
    echo 2. Ejecutar este script de nuevo
    echo.
)

echo ========================================
pause
