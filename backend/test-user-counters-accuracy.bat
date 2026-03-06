@echo off
REM Test de precisión de contadores por usuario
REM Compara datos del backend con la web de la impresora

echo ========================================
echo TEST DE PRECISION - CONTADORES USUARIO
echo ========================================
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar test
python test_user_counters_accuracy.py %1

pause
