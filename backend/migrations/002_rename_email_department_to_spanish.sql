-- Migración 002: Renombrar campos email y department a español
-- Fecha: 2026-02-27
-- Descripción: Renombra email → empresa y department → centro_costos para mayor claridad semántica

-- 1. Eliminar el índice UNIQUE de email (múltiples usuarios pueden tener la misma empresa)
DROP INDEX IF EXISTS ix_users_email;

-- 2. Renombrar columna email a empresa
ALTER TABLE users RENAME COLUMN email TO empresa;

-- 3. Renombrar columna department a centro_costos
ALTER TABLE users RENAME COLUMN department TO centro_costos;

-- 4. Crear índice normal (no único) para empresa para mejorar búsquedas
CREATE INDEX IF NOT EXISTS ix_users_empresa ON users(empresa);

-- 5. Crear índice para centro_costos para mejorar búsquedas
CREATE INDEX IF NOT EXISTS ix_users_centro_costos ON users(centro_costos);

-- Verificar cambios
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND column_name IN ('empresa', 'centro_costos')
ORDER BY ordinal_position;
