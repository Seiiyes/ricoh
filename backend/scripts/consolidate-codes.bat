@echo off
chcp 65001 >nul
echo ========================================
echo Consolidacion de Codigos Duplicados
echo ========================================
echo.
echo Este script consolidara los codigos de usuario
echo cambiando codigos sin cero al formato de 4 digitos
echo Ejemplo: 931 -^> 0931, 455 -^> 0455
echo.
echo IMPORTANTE: Asegurate de tener backup de la base de datos
echo.
pause

cd /d "%~dp0.."
call venv\Scripts\activate.bat
python scripts\consolidate_duplicate_codes.py

echo.
echo ========================================
echo Proceso completado
echo ========================================
pause
