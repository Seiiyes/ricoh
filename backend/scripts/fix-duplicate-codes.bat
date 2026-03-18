@echo off
echo ========================================
echo Correccion de Codigos Duplicados
echo ========================================
echo.
echo Este script normalizara los codigos de usuario
echo eliminando ceros al inicio (0455 -^> 455)
echo.
echo IMPORTANTE: Haz backup de la base de datos antes de continuar
echo.
pause

cd /d "%~dp0\.."
call venv\Scripts\activate.bat
python scripts\fix_duplicate_user_codes.py

echo.
echo ========================================
echo Proceso completado
echo ========================================
pause
