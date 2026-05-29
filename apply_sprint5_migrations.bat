@echo off
echo ========================================
echo   Aplicando Migraciones Sprint 5
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
docker ps | findstr ricoh-db >nul
if errorlevel 1 (
    echo ERROR: El contenedor de base de datos no esta corriendo
    echo Ejecuta: docker-compose -f docker-compose-db-only.yml up -d
    pause
    exit /b 1
)

echo Aplicando migración 012: Índices estratégicos...
docker exec -i ricoh-db psql -U ricoh_admin -d ricoh_fleet < backend\db\migrations\012_indices_dashboard_reportes.sql
if errorlevel 1 (
    echo ERROR al aplicar migración 012
    pause
    exit /b 1
)
echo ✅ Migración 012 aplicada

echo.
echo Aplicando migración 013: Funciones almacenadas...
docker exec -i ricoh-db psql -U ricoh_admin -d ricoh_fleet < backend\db\migrations\013_funciones_dashboard_reportes.sql
if errorlevel 1 (
    echo ERROR al aplicar migración 013
    pause
    exit /b 1
)
echo ✅ Migración 013 aplicada

echo.
echo Aplicando migración 014: Tabla de auditoría...
docker exec -i ricoh-db psql -U ricoh_admin -d ricoh_fleet < backend\db\migrations\014_tabla_auditoria.sql
if errorlevel 1 (
    echo ERROR al aplicar migración 014
    pause
    exit /b 1
)
echo ✅ Migración 014 aplicada

echo.
echo Aplicando migración 015: Top consumo por usuario (dashboard)...
docker exec -i ricoh-db psql -U ricoh_admin -d ricoh_fleet < backend\db\migrations\015_top_consumo_usuarios_dashboard.sql
if errorlevel 1 (
    echo ERROR al aplicar migración 015
    pause
    exit /b 1
)
echo ✅ Migración 015 aplicada

echo.
echo ========================================
echo   Migraciones aplicadas exitosamente
echo ========================================
echo.
echo Verificando migraciones...
echo.

REM Verificar índices
echo Verificando índices...
docker exec ricoh-db psql -U ricoh_admin -d ricoh_fleet -c "SELECT COUNT(*) as indices_creados FROM pg_indexes WHERE indexname LIKE 'idx_%%' AND schemaname = 'public';"

echo.
echo Verificando funciones...
docker exec ricoh-db psql -U ricoh_admin -d ricoh_fleet -c "SELECT routine_name FROM information_schema.routines WHERE routine_type = 'FUNCTION' AND routine_schema = 'public' AND routine_name LIKE 'get_%%' ORDER BY routine_name;"

echo.
echo Verificando tabla de auditoría...
docker exec ricoh-db psql -U ricoh_admin -d ricoh_fleet -c "SELECT table_name FROM information_schema.tables WHERE table_name = 'auditoria_sistema';"

echo.
pause
