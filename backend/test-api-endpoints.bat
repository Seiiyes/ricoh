@echo off
REM ================================================================================
REM Script para probar los endpoints de la API de contadores
REM Requiere que el servidor esté corriendo
REM ================================================================================

echo.
echo ================================================================================
echo 🧪 TEST DE ENDPOINTS DE LA API DE CONTADORES
echo ================================================================================
echo.
echo ⚠️  IMPORTANTE: El servidor debe estar corriendo en http://localhost:8000
echo    Si no está corriendo, ejecuta: start-api-server.bat
echo.

REM Activar entorno virtual y ejecutar tests
call venv\Scripts\activate.bat
python test_api_endpoints.py

pause
