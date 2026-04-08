-- Migración 016: Agregar constraint UNIQUE a codigo_de_usuario
-- Fecha: 2026-04-08
-- Descripción: Previene la creación de usuarios duplicados con el mismo código

-- IMPORTANTE: Ejecutar script de consolidación ANTES de esta migración:
-- python backend/scripts/consolidate_duplicate_users.py

BEGIN;

-- 1. Verificar que no hay duplicados antes de agregar constraint
DO $$
DECLARE
    duplicate_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO duplicate_count
    FROM (
        SELECT codigo_de_usuario, COUNT(*) as count
        FROM users
        GROUP BY codigo_de_usuario
        HAVING COUNT(*) > 1
    ) duplicates;
    
    IF duplicate_count > 0 THEN
        RAISE EXCEPTION 'Aún hay % códigos de usuario duplicados. Ejecutar script de consolidación primero.', duplicate_count;
    END IF;
    
    RAISE NOTICE '✓ Verificación exitosa: No hay códigos duplicados';
END $$;

-- 2. Agregar constraint UNIQUE a codigo_de_usuario
ALTER TABLE users 
ADD CONSTRAINT users_codigo_de_usuario_unique 
UNIQUE (codigo_de_usuario);

-- 3. Agregar comentario al campo
COMMENT ON COLUMN users.codigo_de_usuario IS 
'Código único de usuario (8 dígitos). DEBE estar normalizado sin ceros a la izquierda. Ej: "547" no "0547"';

-- 4. Verificar constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM pg_constraint 
        WHERE conname = 'users_codigo_de_usuario_unique'
    ) THEN
        RAISE NOTICE '✓ Constraint UNIQUE agregado exitosamente';
    ELSE
        RAISE EXCEPTION 'Error: Constraint UNIQUE no fue creado';
    END IF;
END $$;

COMMIT;

-- Resumen de cambios:
-- ✓ Constraint UNIQUE en users.codigo_de_usuario
-- ✓ Comentario documentando normalización requerida
-- ✓ Verificaciones de integridad

-- Siguiente paso:
-- Actualizar código de UserSyncService para normalizar códigos antes de buscar/crear usuarios
