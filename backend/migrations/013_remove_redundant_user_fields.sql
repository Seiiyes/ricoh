-- Migración 013: Eliminar campos redundantes de usuario
-- Fecha: 2026-04-08
-- Descripción: Elimina codigo_usuario y nombre_usuario de contadores y cierres
--              ya que esta información está normalizada en la tabla users

-- ============================================================================
-- VERIFICACIONES PREVIAS
-- ============================================================================

-- Verificar que todos los registros tienen user_id
DO $$
DECLARE
    sin_user_id_contadores INTEGER;
    sin_user_id_cierres INTEGER;
BEGIN
    SELECT COUNT(*) INTO sin_user_id_contadores 
    FROM contadores_usuario 
    WHERE user_id IS NULL;
    
    SELECT COUNT(*) INTO sin_user_id_cierres 
    FROM cierres_mensuales_usuarios 
    WHERE user_id IS NULL;
    
    IF sin_user_id_contadores > 0 THEN
        RAISE EXCEPTION 'ERROR: % registros en contadores_usuario sin user_id. Ejecutar sincronización primero.', sin_user_id_contadores;
    END IF;
    
    IF sin_user_id_cierres > 0 THEN
        RAISE EXCEPTION 'ERROR: % registros en cierres_mensuales_usuarios sin user_id. Ejecutar sincronización primero.', sin_user_id_cierres;
    END IF;
    
    RAISE NOTICE '✓ Verificación exitosa: Todos los registros tienen user_id';
END $$;

-- ============================================================================
-- BACKUP DE SEGURIDAD (crear tabla temporal con datos)
-- ============================================================================

-- Backup de contadores_usuario (solo codigo y nombre)
CREATE TABLE IF NOT EXISTS _backup_contadores_usuario_campos (
    id INTEGER,
    codigo_usuario VARCHAR(8),
    nombre_usuario VARCHAR(100),
    user_id INTEGER,
    created_at TIMESTAMP
);

INSERT INTO _backup_contadores_usuario_campos (id, codigo_usuario, nombre_usuario, user_id, created_at)
SELECT id, codigo_usuario, nombre_usuario, user_id, NOW()
FROM contadores_usuario;

-- Backup de cierres_mensuales_usuarios (solo codigo y nombre)
CREATE TABLE IF NOT EXISTS _backup_cierres_usuarios_campos (
    id INTEGER,
    codigo_usuario VARCHAR(8),
    nombre_usuario VARCHAR(100),
    user_id INTEGER,
    created_at TIMESTAMP
);

INSERT INTO _backup_cierres_usuarios_campos (id, codigo_usuario, nombre_usuario, user_id, created_at)
SELECT id, codigo_usuario, nombre_usuario, user_id, NOW()
FROM cierres_mensuales_usuarios;

-- ============================================================================
-- ELIMINAR VISTAS EXISTENTES QUE DEPENDEN DE LAS COLUMNAS
-- ============================================================================

-- Eliminar vistas existentes
DROP VIEW IF EXISTS v_contadores_usuario CASCADE;
DROP VIEW IF EXISTS v_cierres_mensuales_usuarios CASCADE;

-- ============================================================================
-- ELIMINAR ÍNDICES QUE USAN LAS COLUMNAS
-- ============================================================================

-- Eliminar índices en contadores_usuario
DROP INDEX IF EXISTS idx_contadores_usuario_codigo;
DROP INDEX IF EXISTS idx_contadores_usuario_codigo_usuario;

-- Eliminar índices en cierres_mensuales_usuarios
DROP INDEX IF EXISTS idx_cierres_usuarios_codigo;
DROP INDEX IF EXISTS idx_cierres_usuarios_codigo_usuario;

-- ============================================================================
-- HACER user_id NOT NULL (ahora es obligatorio)
-- ============================================================================

-- Hacer user_id NOT NULL en contadores_usuario
ALTER TABLE contadores_usuario 
ALTER COLUMN user_id SET NOT NULL;

-- Hacer user_id NOT NULL en cierres_mensuales_usuarios
ALTER TABLE cierres_mensuales_usuarios 
ALTER COLUMN user_id SET NOT NULL;

-- ============================================================================
-- ELIMINAR COLUMNAS REDUNDANTES
-- ============================================================================

-- Eliminar columnas de contadores_usuario
ALTER TABLE contadores_usuario 
DROP COLUMN IF EXISTS codigo_usuario,
DROP COLUMN IF EXISTS nombre_usuario;

-- Eliminar columnas de cierres_mensuales_usuarios
ALTER TABLE cierres_mensuales_usuarios 
DROP COLUMN IF EXISTS codigo_usuario,
DROP COLUMN IF EXISTS nombre_usuario;

-- ============================================================================
-- CREAR VISTAS DE COMPATIBILIDAD
-- ============================================================================

-- Vista para contadores_usuario con campos de usuario
CREATE OR REPLACE VIEW v_contadores_usuario_completo AS
SELECT 
    cu.*,
    u.codigo_de_usuario as codigo_usuario,
    u.name as nombre_usuario,
    u.smb_path,
    u.centro_costos
FROM contadores_usuario cu
JOIN users u ON cu.user_id = u.id;

-- Vista para cierres_mensuales_usuarios con campos de usuario
CREATE OR REPLACE VIEW v_cierres_usuarios_completo AS
SELECT 
    cmu.*,
    u.codigo_de_usuario as codigo_usuario,
    u.name as nombre_usuario,
    u.smb_path,
    u.centro_costos
FROM cierres_mensuales_usuarios cmu
JOIN users u ON cmu.user_id = u.id;

-- ============================================================================
-- VERIFICACIONES FINALES
-- ============================================================================

DO $$
DECLARE
    count_contadores INTEGER;
    count_cierres INTEGER;
    count_backup_contadores INTEGER;
    count_backup_cierres INTEGER;
BEGIN
    -- Contar registros actuales
    SELECT COUNT(*) INTO count_contadores FROM contadores_usuario;
    SELECT COUNT(*) INTO count_cierres FROM cierres_mensuales_usuarios;
    
    -- Contar registros en backup
    SELECT COUNT(*) INTO count_backup_contadores FROM _backup_contadores_usuario_campos;
    SELECT COUNT(*) INTO count_backup_cierres FROM _backup_cierres_usuarios_campos;
    
    -- Verificar que no se perdieron registros
    IF count_contadores != count_backup_contadores THEN
        RAISE EXCEPTION 'ERROR: Pérdida de datos en contadores_usuario. Actual: %, Backup: %', 
            count_contadores, count_backup_contadores;
    END IF;
    
    IF count_cierres != count_backup_cierres THEN
        RAISE EXCEPTION 'ERROR: Pérdida de datos en cierres_mensuales_usuarios. Actual: %, Backup: %', 
            count_cierres, count_backup_cierres;
    END IF;
    
    RAISE NOTICE '✓ Migración completada exitosamente';
    RAISE NOTICE '  - contadores_usuario: % registros', count_contadores;
    RAISE NOTICE '  - cierres_mensuales_usuarios: % registros', count_cierres;
    RAISE NOTICE '  - Backups creados en tablas _backup_*';
    RAISE NOTICE '  - Vistas de compatibilidad creadas: v_contadores_usuario_completo, v_cierres_usuarios_completo';
END $$;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================

-- 1. Las tablas de backup (_backup_*) se pueden eliminar después de verificar
--    que todo funciona correctamente (esperar 1-2 semanas)
--
-- 2. Las vistas de compatibilidad (v_*_completo) permiten acceder a los datos
--    de usuario sin modificar queries existentes
--
-- 3. Para restaurar los campos (si es necesario):
--    ALTER TABLE contadores_usuario ADD COLUMN codigo_usuario VARCHAR(8);
--    ALTER TABLE contadores_usuario ADD COLUMN nombre_usuario VARCHAR(100);
--    UPDATE contadores_usuario cu SET 
--        codigo_usuario = b.codigo_usuario,
--        nombre_usuario = b.nombre_usuario
--    FROM _backup_contadores_usuario_campos b
--    WHERE cu.id = b.id;
--
-- 4. user_id ahora es NOT NULL, garantizando integridad referencial
