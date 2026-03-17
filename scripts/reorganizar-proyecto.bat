@echo off
echo ========================================
echo REORGANIZACION DEL PROYECTO
echo ========================================
echo.
echo Este script reorganizara los archivos del proyecto
echo moviendo archivos temporales a carpetas apropiadas.
echo.
echo IMPORTANTE: Se recomienda hacer backup antes de continuar.
echo.
pause

echo.
echo [1/5] Creando estructura de carpetas...
echo.

REM Raiz
if not exist "scripts" mkdir scripts
if not exist "scripts\importacion" mkdir scripts\importacion
if not exist "scripts\verificacion" mkdir scripts\verificacion
if not exist "scripts\utilidades" mkdir scripts\utilidades

REM Docs
if not exist "docs\desarrollo" mkdir docs\desarrollo
if not exist "docs\desarrollo\importacion" mkdir docs\desarrollo\importacion
if not exist "docs\desarrollo\analisis" mkdir docs\desarrollo\analisis
if not exist "docs\desarrollo\verificacion" mkdir docs\desarrollo\verificacion

REM Backend
if not exist "backend\scripts" mkdir backend\scripts
if not exist "backend\scripts\analisis" mkdir backend\scripts\analisis
if not exist "backend\scripts\verificacion" mkdir backend\scripts\verificacion
if not exist "backend\scripts\importacion" mkdir backend\scripts\importacion
if not exist "backend\scripts\utilidades" mkdir backend\scripts\utilidades
if not exist "backend\data" mkdir backend\data

echo OK - Carpetas creadas

echo.
echo [2/5] Moviendo archivos Markdown...
echo.

REM Mover MD de analisis
move /Y ANALISIS_*.md docs\desarrollo\analisis\ 2>nul

REM Mover MD de verificacion
move /Y VERIFICACION_*.md docs\desarrollo\verificacion\ 2>nul

REM Mover MD de importacion
move /Y IMPORTACION_*.md docs\desarrollo\importacion\ 2>nul
move /Y CONFIRMACION_*.md docs\desarrollo\importacion\ 2>nul
move /Y INSTRUCCIONES_*.md docs\desarrollo\importacion\ 2>nul
move /Y LISTO_*.md docs\desarrollo\importacion\ 2>nul

REM Mover otros MD
move /Y RESUMEN_*.md docs\desarrollo\ 2>nul
move /Y CAMBIOS_*.md docs\desarrollo\ 2>nul
move /Y CAPACIDADES_*.md docs\desarrollo\ 2>nul
move /Y CONTADORES_*.md docs\desarrollo\ 2>nul
move /Y ESTADO_*.md docs\desarrollo\ 2>nul
move /Y EXPORTACION_*.md docs\desarrollo\ 2>nul
move /Y MAPEO_*.md docs\desarrollo\ 2>nul
move /Y MEJORAS_*.md docs\desarrollo\ 2>nul
move /Y NUEVO_*.md docs\desarrollo\ 2>nul
move /Y PLAN_*.md docs\desarrollo\ 2>nul
move /Y PROBLEMA_*.md docs\desarrollo\ 2>nul
move /Y SOLUCION_*.md docs\desarrollo\ 2>nul
move /Y TRABAJO_*.md docs\desarrollo\ 2>nul

echo OK - Archivos MD movidos

echo.
echo [3/5] Moviendo scripts Python del backend...
echo.

REM Analisis
move /Y backend\analisis_*.py backend\scripts\analisis\ 2>nul
move /Y backend\analizar_*.py backend\scripts\analisis\ 2>nul

REM Verificacion
move /Y backend\verificacion_*.py backend\scripts\verificacion\ 2>nul
move /Y backend\verificar_*.py backend\scripts\verificacion\ 2>nul

REM Importacion
move /Y backend\importar_*.py backend\scripts\importacion\ 2>nul
move /Y backend\pre_importacion_*.py backend\scripts\importacion\ 2>nul
move /Y backend\validar_estructura_*.py backend\scripts\importacion\ 2>nul
move /Y backend\validar_importacion_*.py backend\scripts\importacion\ 2>nul

REM Utilidades
move /Y backend\aplicar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\borrar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\comparar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\contar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\corregir_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\debug_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\estado_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\extraer_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\listar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\mapeo_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\probar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\revisar_*.py backend\scripts\utilidades\ 2>nul
move /Y backend\test_*.py backend\scripts\utilidades\ 2>nul

REM Data
move /Y backend\contadores_usuarios_completo.json backend\data\ 2>nul

echo OK - Scripts Python movidos

echo.
echo [4/5] Moviendo archivos .bat...
echo.

REM Raiz a scripts
move /Y comparar-csv.bat scripts\ 2>nul
move /Y estado-importacion.bat scripts\ 2>nul
move /Y importar-*.bat scripts\importacion\ 2>nul
move /Y validar-importacion.bat scripts\ 2>nul
move /Y verificar-importacion.bat scripts\ 2>nul

REM Backend
move /Y backend\comparar-csv-db.bat backend\scripts\ 2>nul
move /Y backend\listar-impresoras.bat backend\scripts\ 2>nul
move /Y backend\start-api-server.bat backend\scripts\ 2>nul
move /Y backend\start-backend-venv.bat backend\scripts\ 2>nul
move /Y backend\start-backend.bat backend\scripts\ 2>nul
move /Y backend\verificar-datos.bat backend\scripts\ 2>nul

echo OK - Archivos .bat movidos

echo.
echo [5/5] Eliminando archivos temporales...
echo.

del /Q test_lectura_250.py 2>nul
del /Q test_parser_252.py 2>nul

echo OK - Archivos temporales eliminados

echo.
echo ========================================
echo REORGANIZACION COMPLETADA
echo ========================================
echo.
echo Resumen:
echo - Archivos MD movidos a docs/desarrollo/
echo - Scripts Python movidos a backend/scripts/
echo - Archivos .bat movidos a scripts/
echo - Archivos temporales eliminados
echo.
echo IMPORTANTE: Revisa que todo funcione correctamente
echo antes de hacer commit de los cambios.
echo.
pause
