-- Migration 012: Normalizar referencias de usuarios en tablas de cierres y contadores
-- Objetivo: Reemplazar codigo_usuario/nombre_usuario por user_id (FK)
-- Beneficios: Integridad referencial, mejor rendimiento, menor espacio

BEGIN;

-- ============================================================================
-- PASO 1: Agregar columna user_id a cierres_mensuales_usuarios
-- ============================================================================

ALTER TABLE cierres_mensuales_usuarios 
ADD COLUMN user_id INTEGER;

COMMENT ON COLUMN cierres_mensuales_usuarios.user_id IS 
'FK a users.id - Reemplaza codigo_usuario/nombre_usuario para normalización';

-- ============================================================================
-- PASO 2: Poblar user_id en cierres_mensuales_usuarios
-- ============================================================================

-- Actualizar registros que tienen match en users
UPDATE cierres_mensuales_usuarios cmu
SET user_id = u.id
FROM users u
WHERE u.codigo_de_usuario = cmu.codigo_usuario;

-- Verificar cuántos quedaron sin match
DO $$
DECLARE
    sin_match INTEGER;
BEGIN
    SELECT COUNT(*) INTO sin_match
    FROM cierres_mensuales_usuarios
    WHERE user_id IS NULL;
    
    RAISE NOTICE 'Registros en cierres_mensuales_usuarios sin user_id: %', sin_match;
    
    IF sin_match > 0 THEN
        RAISE NOTICE 'Estos son usuarios históricos que ya no existen en la tabla users';
        RAISE NOTICE 'Se mantendrán codigo_usuario y nombre_usuario para referencia histórica';
    END IF;
END $$;

-- ============================================================================
-- PASO 3: Agregar columna user_id a contadores_usuario
-- ============================================================================

ALTER TABLE contadores_usuario 
ADD COLUMN user_id INTEGER;

COMMENT ON COLUMN contadores_usuario.user_id IS 
'FK a users.id - Reemplaza codigo_usuario/nombre_usuario para normalización';

-- ============================================================================
-- PASO 4: Poblar user_id en contadores_usuario
-- ============================================================================

-- Actualizar registros que tienen match en users
UPDATE contadores_usuario cu
SET user_id = u.id
FROM users u
WHERE u.codigo_de_usuario = cu.codigo_usuario;

-- Verificar cuántos quedaron sin match
DO $$
DECLARE
    sin_match INTEGER;
BEGIN
    SELECT COUNT(*) INTO sin_match
    FROM contadores_usuario
    WHERE user_id IS NULL;
    
    RAISE NOTICE 'Registros en contadores_usuario sin user_id: %', sin_match;
END $$;

-- ============================================================================
-- PASO 5: Crear índices en user_id
-- ============================================================================

CREATE INDEX idx_cierres_usuarios_user_id ON cierres_mensuales_usuarios(user_id);
CREATE INDEX idx_contadores_usuario_user_id ON contadores_usuario(user_id);

-- Índice compuesto para consultas comunes
CREATE INDEX idx_contadores_usuario_lookup_v2 ON contadores_usuario(printer_id, user_id, created_at DESC);

-- ============================================================================
-- PASO 6: Agregar FK constraints (solo para registros con user_id)
-- ============================================================================

-- FK para cierres_mensuales_usuarios
ALTER TABLE cierres_mensuales_usuarios
ADD CONSTRAINT fk_cierres_usuarios_user_id 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE SET NULL;  -- Si se elimina el usuario, mantener el registro histórico

-- FK para contadores_usuario
ALTER TABLE contadores_usuario
ADD CONSTRAINT fk_contadores_usuario_user_id 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE SET NULL;  -- Si se elimina el usuario, mantener el registro histórico

-- ============================================================================
-- PASO 7: Normalizar campos de auditoría en cierres_mensuales
-- ============================================================================

-- Agregar columnas para FK a admin_users
ALTER TABLE cierres_mensuales
ADD COLUMN cerrado_por_admin_id INTEGER,
ADD COLUMN modified_by_admin_id INTEGER;

COMMENT ON COLUMN cierres_mensuales.cerrado_por_admin_id IS 
'FK a admin_users.id - Usuario admin que realizó el cierre';

COMMENT ON COLUMN cierres_mensuales.modified_by_admin_id IS 
'FK a admin_users.id - Usuario admin que modificó el cierre';

-- Intentar mapear valores existentes (si hay coincidencias)
UPDATE cierres_mensuales cm
SET cerrado_por_admin_id = au.id
FROM admin_users au
WHERE au.username = cm.cerrado_por
   OR au.nombre_completo = cm.cerrado_por;

UPDATE cierres_mensuales cm
SET modified_by_admin_id = au.id
FROM admin_users au
WHERE au.username = cm.modified_by
   OR au.nombre_completo = cm.modified_by;

-- Agregar FK constraints
ALTER TABLE cierres_mensuales
ADD CONSTRAINT fk_cierres_cerrado_por_admin 
FOREIGN KEY (cerrado_por_admin_id) 
REFERENCES admin_users(id) 
ON DELETE SET NULL;

ALTER TABLE cierres_mensuales
ADD CONSTRAINT fk_cierres_modified_by_admin 
FOREIGN KEY (modified_by_admin_id) 
REFERENCES admin_users(id) 
ON DELETE SET NULL;

-- Crear índices
CREATE INDEX idx_cierres_cerrado_por_admin ON cierres_mensuales(cerrado_por_admin_id);
CREATE INDEX idx_cierres_modified_by_admin ON cierres_mensuales(modified_by_admin_id);

-- ============================================================================
-- PASO 8: Crear vistas para compatibilidad con código existente
-- ============================================================================

-- Vista que combina user_id con codigo_usuario/nombre_usuario
CREATE OR REPLACE VIEW v_cierres_mensuales_usuarios AS
SELECT 
    cmu.*,
    COALESCE(u.codigo_de_usuario, cmu.codigo_usuario) as codigo_usuario_actual,
    COALESCE(u.name, cmu.nombre_usuario) as nombre_usuario_actual,
    u.name as nombre_usuario_sistema,
    u.centro_costos
FROM cierres_mensuales_usuarios cmu
LEFT JOIN users u ON cmu.user_id = u.id;

COMMENT ON VIEW v_cierres_mensuales_usuarios IS 
'Vista que combina datos normalizados (user_id) con datos históricos (codigo_usuario/nombre_usuario)';

-- Vista para contadores_usuario
CREATE OR REPLACE VIEW v_contadores_usuario AS
SELECT 
    cu.*,
    COALESCE(u.codigo_de_usuario, cu.codigo_usuario) as codigo_usuario_actual,
    COALESCE(u.name, cu.nombre_usuario) as nombre_usuario_actual,
    u.name as nombre_usuario_sistema,
    u.centro_costos,
    u.empresa_id
FROM contadores_usuario cu
LEFT JOIN users u ON cu.user_id = u.id;

COMMENT ON VIEW v_contadores_usuario IS 
'Vista que combina datos normalizados (user_id) con datos históricos (codigo_usuario/nombre_usuario)';

-- ============================================================================
-- PASO 9: Estadísticas finales
-- ============================================================================

DO $$
DECLARE
    cierres_con_fk INTEGER;
    cierres_sin_fk INTEGER;
    contadores_con_fk INTEGER;
    contadores_sin_fk INTEGER;
    cierres_auditoria INTEGER;
BEGIN
    -- Contar registros con FK en cierres
    SELECT COUNT(*) INTO cierres_con_fk
    FROM cierres_mensuales_usuarios
    WHERE user_id IS NOT NULL;
    
    SELECT COUNT(*) INTO cierres_sin_fk
    FROM cierres_mensuales_usuarios
    WHERE user_id IS NULL;
    
    -- Contar registros con FK en contadores
    SELECT COUNT(*) INTO contadores_con_fk
    FROM contadores_usuario
    WHERE user_id IS NOT NULL;
    
    SELECT COUNT(*) INTO contadores_sin_fk
    FROM contadores_usuario
    WHERE user_id IS NULL;
    
    -- Contar cierres con auditoría normalizada
    SELECT COUNT(*) INTO cierres_auditoria
    FROM cierres_mensuales
    WHERE cerrado_por_admin_id IS NOT NULL;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'MIGRACIÓN 012 COMPLETADA';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'cierres_mensuales_usuarios:';
    RAISE NOTICE '  - Con user_id: %', cierres_con_fk;
    RAISE NOTICE '  - Sin user_id (históricos): %', cierres_sin_fk;
    RAISE NOTICE '';
    RAISE NOTICE 'contadores_usuario:';
    RAISE NOTICE '  - Con user_id: %', contadores_con_fk;
    RAISE NOTICE '  - Sin user_id (históricos): %', contadores_sin_fk;
    RAISE NOTICE '';
    RAISE NOTICE 'cierres_mensuales (auditoría):';
    RAISE NOTICE '  - Con cerrado_por_admin_id: %', cierres_auditoria;
    RAISE NOTICE '';
    RAISE NOTICE 'NOTA: Los campos codigo_usuario y nombre_usuario';
    RAISE NOTICE 'se mantienen para referencia histórica.';
    RAISE NOTICE 'El código nuevo debe usar user_id.';
    RAISE NOTICE '========================================';
END $$;

COMMIT;

-- ============================================================================
-- NOTAS IMPORTANTES PARA EL DESARROLLO
-- ============================================================================

-- 1. NUEVOS REGISTROS: Siempre insertar user_id cuando se cree un contador o cierre
--    Ejemplo:
--    INSERT INTO contadores_usuario (printer_id, user_id, codigo_usuario, nombre_usuario, ...)
--    VALUES (1, 5, '7104', 'JUAN LIZARAZO', ...);

-- 2. CONSULTAS: Preferir JOIN por user_id en lugar de codigo_usuario
--    ANTES:
--    SELECT * FROM contadores_usuario cu
--    JOIN users u ON u.codigo_de_usuario = cu.codigo_usuario;
--    
--    DESPUÉS:
--    SELECT * FROM contadores_usuario cu
--    JOIN users u ON u.id = cu.user_id;

-- 3. USUARIOS HISTÓRICOS: Los registros con user_id NULL son válidos
--    Representan usuarios que existieron pero fueron eliminados

-- 4. VISTAS: Usar v_contadores_usuario y v_cierres_mensuales_usuarios
--    para obtener datos combinados automáticamente

-- 5. DEPRECACIÓN FUTURA: En una migración posterior se podrían eliminar
--    codigo_usuario y nombre_usuario si ya no se necesitan
