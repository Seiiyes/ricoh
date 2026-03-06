@echo off
REM Test del servicio de contadores
echo ================================================================================
echo TEST DEL SERVICIO DE CONTADORES
echo ================================================================================
echo.

cd /d "%~dp0"

REM Activar entorno virtual
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Ejecutar test
if "%1"=="" (
    python test_counter_service.py single
) else (
    python test_counter_service.py %1
)

echo.
echo ================================================================================
echo Presiona cualquier tecla para salir...
pause >nul
