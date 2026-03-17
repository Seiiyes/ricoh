@echo off
echo ========================================
echo ELIMINACION DE ARCHIVOS TEMPORALES
echo ========================================
echo.
echo Este script eliminara archivos que ya no se necesitan:
echo - Scripts de importacion CSV (completada)
echo - Scripts de analisis CSV (completados)
echo - Scripts de verificacion CSV (completados)
echo - Archivos CSV historicos (ya en BD)
echo - Archivos .bat temporales
echo.
echo TOTAL: ~130 archivos (~8-13 MB)
echo.
echo IMPORTANTE: Esta accion NO se puede deshacer.
echo Se recomienda hacer backup antes de continuar.
echo.
pause

echo.
echo [1/7] Eliminando scripts de importacion...
rd /s /q "backend\scripts\importacion" 2>nul
echo OK

echo.
echo [2/7] Eliminando scripts de analisis...
rd /s /q "backend\scripts\analisis" 2>nul
echo OK

echo.
echo [3/7] Eliminando scripts de verificacion...
rd /s /q "backend\scripts\verificacion" 2>nul
echo OK

echo.
echo [4/7] Eliminando scripts de utilidades temporales...
del /q "backend\scripts\utilidades\aplicar_correccion_contadores.py" 2>nul
del /q "backend\scripts\utilidades\borrar_cierres_enero_febrero.py" 2>nul
del /q "backend\scripts\utilidades\comparar_csv_vs_db_simple.py" 2>nul
del /q "backend\scripts\utilidades\comparar_todos_csv.py" 2>nul
del /q "backend\scripts\utilidades\contar_usuarios_reales.py" 2>nul
del /q "backend\scripts\utilidades\debug_importacion.py" 2>nul
del /q "backend\scripts\utilidades\estado_final_cierres.py" 2>nul
del /q "backend\scripts\utilidades\estado_importacion.py" 2>nul
del /q "backend\scripts\utilidades\extraer_contadores_reales_todos.py" 2>nul
del /q "backend\scripts\utilidades\extraer_todos_contadores_reales.py" 2>nul
del /q "backend\scripts\utilidades\mapeo_detallado_campos.py" 2>nul
del /q "backend\scripts\utilidades\revisar_todos_archivos_csv.py" 2>nul
del /q "backend\scripts\utilidades\test_match_nombres.py" 2>nul
del /q "backend\scripts\utilidades\test_parse_enero.py" 2>nul
echo OK

echo.
echo [5/7] Eliminando archivos CSV historicos...
rd /s /q "docs\CONTADOR IMPRESORAS ENERO" 2>nul
rd /s /q "docs\CONTADOR IMPRESORAS FEBRERO" 2>nul
rd /s /q "docs\CSV_COMPARATIVOS" 2>nul
rd /s /q "docs\COMPARATIVO IMPRESORAS DICIEMBRE - ENERO" 2>nul
rd /s /q "docs\COMPARATIVO IMPRESORAS ENERO - FEBRERO" 2>nul
echo OK

echo.
echo [6/7] Eliminando archivos .bat temporales...
rd /s /q "scripts\importacion" 2>nul
del /q "scripts\comparar-csv.bat" 2>nul
del /q "scripts\estado-importacion.bat" 2>nul
del /q "scripts\validar-importacion.bat" 2>nul
del /q "scripts\verificar-importacion.bat" 2>nul
del /q "backend\scripts\comparar-csv-db.bat" 2>nul
del /q "backend\scripts\verificar-datos.bat" 2>nul
echo OK

echo.
echo [7/7] Eliminando archivos Excel historicos...
del /q "docs\COMPARATIVO FINAL ENERO - FEBRERO.xlsx" 2>nul
del /q "docs\COMPARATIVO FINAL IMPRESORAS DICIEMBRE - ENERO.xlsx" 2>nul
echo OK

echo.
echo ========================================
echo ELIMINACION COMPLETADA
echo ========================================
echo.
echo Archivos eliminados: ~130
echo Espacio liberado: ~8-13 MB
echo.
echo Archivos mantenidos:
echo - Scripts utiles en backend/scripts/utilidades/
echo - Documentacion en docs/desarrollo/
echo - Scripts de inicio (.bat)
echo.
pause
