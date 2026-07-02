@echo off
echo ========================================
echo   Verificando Migraciones Sprint 5
echo ========================================
echo.

REM Verificar si Docker esta corriendo
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta corriendo
    echo Por favor inicia Docker Desktop primero
    pause
    exit /b 1
)

REM Verificar si el contenedor de DB esta corriendo
docker ps | findstr ricoh-postgres >nul
if errorlevel 1 (
    echo ERROR: El contenedor de base de datos no esta corriendo
    echo Ejecuta: docker-compose up -d
    pause
    exit /b 1
)

echo Conectando a la base de datos...
echo.

REM Crear script SQL temporal
echo SELECT '========================================' as ""; > temp_verify.sql
echo SELECT 'VERIFICANDO INDICES (Migracion 012)' as ""; >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT indexname as "Indice" FROM pg_indexes WHERE indexname LIKE 'idx_%%' AND schemaname = 'public' ORDER BY indexname; >> temp_verify.sql
echo SELECT ''; >> temp_verify.sql
echo SELECT 'Total indices encontrados: ' ^|^| COUNT(*)::text as "" FROM pg_indexes WHERE indexname LIKE 'idx_%%' AND schemaname = 'public'; >> temp_verify.sql
echo. >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT 'VERIFICANDO FUNCIONES (Migracion 013)' as ""; >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT routine_name ^|^| '()' as "Funcion" FROM information_schema.routines WHERE routine_type = 'FUNCTION' AND routine_schema = 'public' AND routine_name LIKE 'get_%%' ORDER BY routine_name; >> temp_verify.sql
echo SELECT ''; >> temp_verify.sql
echo SELECT 'Total funciones encontradas: ' ^|^| COUNT(*)::text as "" FROM information_schema.routines WHERE routine_type = 'FUNCTION' AND routine_schema = 'public' AND routine_name LIKE 'get_%%'; >> temp_verify.sql
echo. >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT 'VERIFICANDO TABLA AUDITORIA (Migracion 014)' as ""; >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'auditoria_sistema') THEN 'Tabla auditoria_sistema: EXISTE' ELSE 'Tabla auditoria_sistema: NO EXISTE' END as ""; >> temp_verify.sql
echo SELECT trigger_name ^|^| ' (trigger)' as "Trigger" FROM information_schema.triggers WHERE trigger_schema = 'public' AND trigger_name LIKE 'auditar_%%' ORDER BY trigger_name; >> temp_verify.sql
echo. >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT 'RESUMEN' as ""; >> temp_verify.sql
echo SELECT '========================================' as ""; >> temp_verify.sql
echo SELECT 'Indices: ' ^|^| COUNT(*)::text ^|^| ' / 13 esperados' as "" FROM pg_indexes WHERE indexname LIKE 'idx_%%' AND schemaname = 'public'; >> temp_verify.sql
echo SELECT 'Funciones: ' ^|^| COUNT(*)::text ^|^| ' / 4 esperadas' as "" FROM information_schema.routines WHERE routine_type = 'FUNCTION' AND routine_schema = 'public' AND routine_name LIKE 'get_%%'; >> temp_verify.sql
echo SELECT 'Triggers: ' ^|^| COUNT(*)::text ^|^| ' / 2 esperados' as "" FROM information_schema.triggers WHERE trigger_schema = 'public' AND trigger_name LIKE 'auditar_%%'; >> temp_verify.sql

REM Ejecutar verificación
docker exec -i ricoh-postgres psql -U ricoh_admin -d ricoh_fleet < temp_verify.sql

REM Limpiar archivo temporal
del temp_verify.sql

echo.
echo ========================================
echo   Verificacion completada
echo ========================================
echo.
echo Si faltan migraciones, ejecuta:
echo   apply_sprint5_migrations.bat
echo.
pause
