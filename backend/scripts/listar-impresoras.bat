@echo off
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.
echo Listando impresoras en DB...
python listar_impresoras_db.py
echo.
pause
