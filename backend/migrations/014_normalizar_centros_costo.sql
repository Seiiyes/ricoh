-- Migración 014: Normalizar Centros de Costo por Empresa
-- Descripción: Crea la tabla 'centro_costos' asociada a la empresa, agrega 'centro_costo_id' a la tabla 'users', realiza la migración de datos existentes, elimina la columna antigua 'centro_costos' de texto y recrea las vistas de compatibilidad dependientes.

-- 1. Eliminar vistas existentes de compatibilidad para evitar errores de dependencia al alterar columnas
DROP VIEW IF EXISTS v_contadores_usuario_completo CASCADE;
DROP VIEW IF EXISTS v_cierres_usuarios_completo CASCADE;
DROP VIEW IF EXISTS v_users_completo CASCADE;

-- 2. Crear tabla de centros de costo
CREATE TABLE IF NOT EXISTS centro_costos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT uq_centro_costo_empresa_nombre UNIQUE (empresa_id, nombre)
);

-- Crear índice para optimizar consultas de multi-tenancy
CREATE INDEX IF NOT EXISTS idx_centro_costos_empresa_nombre ON centro_costos(empresa_id, nombre);

-- 3. Agregar columna centro_costo_id a la tabla de usuarios
ALTER TABLE users ADD COLUMN IF NOT EXISTS centro_costo_id INTEGER REFERENCES centro_costos(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_users_centro_costo_id ON users(centro_costo_id);

-- 4. Migrar datos existentes (DML)
-- Inserta centros de costos únicos mapeados de los usuarios que ya tienen una empresa asociada
INSERT INTO centro_costos (nombre, empresa_id)
SELECT DISTINCT centro_costos, empresa_id 
FROM users 
WHERE centro_costos IS NOT NULL 
  AND centro_costos != '' 
  AND empresa_id IS NOT NULL
ON CONFLICT (empresa_id, nombre) DO NOTHING;

-- 5. Vincular usuarios existentes a sus correspondientes registros de la tabla normalizada
UPDATE users u
SET centro_costo_id = cc.id
FROM centro_costos cc
WHERE u.centro_costos = cc.nombre 
  AND u.empresa_id = cc.empresa_id
  AND u.centro_costos IS NOT NULL 
  AND u.empresa_id IS NOT NULL;

-- 6. Eliminar la columna de texto antigua 'centro_costos' de la tabla 'users' para evitar duplicidad
ALTER TABLE users DROP COLUMN IF EXISTS centro_costos;

-- 7. Recrear vistas de compatibilidad dependientes, obteniendo el campo 'centro_costos' estructurado vía LEFT JOIN

-- Vista v_users_completo (normalizada con campos SMB y centro de costos unificado)
CREATE OR REPLACE VIEW v_users_completo AS
SELECT 
    u.id,
    u.name,
    u.codigo_de_usuario,
    u.network_username,
    u.network_password_encrypted,
    u.smb_server,
    u.smb_port,
    u.smb_path,
    u.func_copier,
    u.func_copier_color,
    u.func_printer,
    u.func_printer_color,
    u.func_document_server,
    u.func_fax,
    u.func_scanner,
    u.func_browser,
    u.empresa_id,
    u.centro_costo_id,
    u.smb_server_id,
    u.network_credential_id,
    u.is_active,
    u.created_at,
    u.updated_at,
    s.server_address as smb_server_address,
    s.port as smb_server_port,
    nc.username as network_credential_username,
    cc.nombre as centro_costos
FROM users u
JOIN smb_servers s ON u.smb_server_id = s.id
JOIN network_credentials nc ON u.network_credential_id = nc.id
LEFT JOIN centro_costos cc ON u.centro_costo_id = cc.id;

-- Vista v_contadores_usuario_completo (normalizada para asociar consumo con el nombre del centro de costos)
CREATE OR REPLACE VIEW v_contadores_usuario_completo AS
SELECT 
    cu.*,
    u.codigo_de_usuario as codigo_usuario,
    u.name as nombre_usuario,
    u.smb_path,
    cc.nombre as centro_costos
FROM contadores_usuario cu
JOIN users u ON cu.user_id = u.id
LEFT JOIN centro_costos cc ON u.centro_costo_id = cc.id;

-- Vista v_cierres_usuarios_completo (normalizada para asociar cierres con el nombre del centro de costos)
CREATE OR REPLACE VIEW v_cierres_usuarios_completo AS
SELECT 
    cmu.*,
    u.codigo_de_usuario as codigo_usuario,
    u.name as nombre_usuario,
    u.smb_path,
    cc.nombre as centro_costos
FROM cierres_mensuales_usuarios cmu
JOIN users u ON cmu.user_id = u.id
LEFT JOIN centro_costos cc ON u.centro_costo_id = cc.id;
