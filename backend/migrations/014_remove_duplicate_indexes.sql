-- Migración 014: Eliminar índices duplicados
-- Fecha: 2026-04-08
-- Descripción: Elimina índices duplicados que consumen espacio y afectan performance de escrituras

-- ============================================================================
-- ANÁLISIS PREVIO
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'MIGRACIÓN 014: Eliminación de Índices Duplicados';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Objetivo: Eliminar índices redundantes que duplican funcionalidad';
    RAISE NOTICE 'Impacto: Ahorro de ~200-300 KB, mejora en performance de escrituras';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- TABLA: contadores_usuario
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Procesando tabla: contadores_usuario';
    RAISE NOTICE '-------------------------------------------------------------------';
END $$;

-- Índice duplicado en printer_id
-- MANTENER: idx_contadores_usuario_printer_id (nombre más descriptivo)
-- ELIMINAR: ix_contadores_usuario_printer_id (prefijo genérico)
DROP INDEX IF EXISTS ix_contadores_usuario_printer_id;

-- Índice duplicado en fecha_lectura
-- MANTENER: idx_contadores_usuario_fecha_lectura (nombre más descriptivo)
-- ELIMINAR: ix_contadores_usuario_fecha_lectura (prefijo genérico)
DROP INDEX IF EXISTS ix_contadores_usuario_fecha_lectura;

-- Índice duplicado en id (PK ya tiene índice automático)
-- ELIMINAR: ix_contadores_usuario_id (redundante con PK)
DROP INDEX IF EXISTS ix_contadores_usuario_id;

DO $$
BEGIN
    RAISE NOTICE '✓ Eliminados 3 índices duplicados en contadores_usuario';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- TABLA: printers
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Procesando tabla: printers';
    RAISE NOTICE '-------------------------------------------------------------------';
END $$;

-- Índice duplicado en serial_number
-- MANTENER: idx_printers_serial_number (nombre más descriptivo)
-- ELIMINAR: ix_printers_serial_number (prefijo genérico)
DROP INDEX IF EXISTS ix_printers_serial_number;

-- Índice duplicado en empresa_id
-- MANTENER: idx_printers_empresa (nombre más descriptivo)
-- ELIMINAR: ix_printers_empresa_id (prefijo genérico)
DROP INDEX IF EXISTS ix_printers_empresa_id;

-- Índice duplicado en hostname
-- ELIMINAR: ix_printers_hostname (no hay otro índice, pero hostname no se usa en búsquedas frecuentes)
-- Verificar uso antes de eliminar
-- DROP INDEX IF EXISTS ix_printers_hostname;

-- Índice duplicado en id (PK ya tiene índice automático)
-- ELIMINAR: ix_printers_id (redundante con PK)
DROP INDEX IF EXISTS ix_printers_id;

DO $$
BEGIN
    RAISE NOTICE '✓ Eliminados 3 índices duplicados en printers';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- TABLA: users
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Procesando tabla: users';
    RAISE NOTICE '-------------------------------------------------------------------';
END $$;

-- Índice duplicado en empresa_id
-- MANTENER: ix_users_empresa (nombre más descriptivo)
-- ELIMINAR: ix_users_empresa_id (prefijo genérico)
DROP INDEX IF EXISTS ix_users_empresa_id;

-- Índice duplicado en id (PK ya tiene índice automático)
-- ELIMINAR: ix_users_id (redundante con PK)
DROP INDEX IF EXISTS ix_users_id;

DO $$
BEGIN
    RAISE NOTICE '✓ Eliminados 2 índices duplicados en users';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================

DO $$
DECLARE
    total_indexes INTEGER;
    contadores_indexes INTEGER;
    printers_indexes INTEGER;
    users_indexes INTEGER;
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'VERIFICACIÓN FINAL';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE '';
    
    -- Contar índices por tabla
    SELECT COUNT(*) INTO contadores_indexes
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'contadores_usuario';
    
    SELECT COUNT(*) INTO printers_indexes
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'printers';
    
    SELECT COUNT(*) INTO users_indexes
    FROM pg_indexes
    WHERE schemaname = 'public' AND tablename = 'users';
    
    total_indexes := contadores_indexes + printers_indexes + users_indexes;
    
    RAISE NOTICE 'Índices restantes:';
    RAISE NOTICE '  - contadores_usuario: % índices', contadores_indexes;
    RAISE NOTICE '  - printers: % índices', printers_indexes;
    RAISE NOTICE '  - users: % índices', users_indexes;
    RAISE NOTICE '  - TOTAL: % índices', total_indexes;
    RAISE NOTICE '';
    RAISE NOTICE '✓ Migración completada exitosamente';
    RAISE NOTICE '✓ Eliminados 8 índices duplicados';
    RAISE NOTICE '✓ Ahorro estimado: ~200-300 KB';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- ANÁLISIS DE ÍNDICES RESTANTES
-- ============================================================================

-- Mostrar índices restantes en tablas principales
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('contadores_usuario', 'printers', 'users')
ORDER BY tablename, indexname;
