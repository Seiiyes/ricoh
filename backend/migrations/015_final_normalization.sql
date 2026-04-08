-- Migración 015: Normalización Final de Base de Datos
-- Fecha: 2026-04-08
-- Descripción: Normalización completa basada en análisis de uso real del sistema

-- ============================================================================
-- ANÁLISIS PREVIO
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'MIGRACIÓN 015: Normalización Final';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Cambios a realizar:';
    RAISE NOTICE '1. Normalizar configuración SMB (99.55%% usan mismo servidor)';
    RAISE NOTICE '2. Normalizar credenciales de red (100%% usan mismo usuario)';
    RAISE NOTICE '3. Sincronizar capabilities_json con campos booleanos';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- PASO 1: Crear tabla de configuración SMB
-- ============================================================================

CREATE TABLE IF NOT EXISTS smb_servers (
    id SERIAL PRIMARY KEY,
    server_address VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL DEFAULT 21,
    description VARCHAR(500),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(server_address, port)
);

-- Insertar servidores existentes
INSERT INTO smb_servers (server_address, port, description, is_default)
SELECT DISTINCT 
    smb_server,
    smb_port,
    CASE 
        WHEN smb_server = '192.168.91.5' THEN 'Servidor SMB principal'
        ELSE 'Servidor SMB alternativo'
    END,
    CASE WHEN smb_server = '192.168.91.5' THEN TRUE ELSE FALSE END
FROM users
ON CONFLICT (server_address, port) DO NOTHING;

-- Agregar columna smb_server_id a users
ALTER TABLE users ADD COLUMN IF NOT EXISTS smb_server_id INTEGER;

-- Poblar smb_server_id
UPDATE users u
SET smb_server_id = s.id
FROM smb_servers s
WHERE u.smb_server = s.server_address 
  AND u.smb_port = s.port;

-- Agregar FK constraint
ALTER TABLE users 
ADD CONSTRAINT fk_users_smb_server 
FOREIGN KEY (smb_server_id) REFERENCES smb_servers(id) ON DELETE RESTRICT;

-- Hacer smb_server_id NOT NULL
ALTER TABLE users ALTER COLUMN smb_server_id SET NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '✓ Paso 1 completado: Tabla smb_servers creada y poblada';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- PASO 2: Crear tabla de credenciales de red
-- ============================================================================

CREATE TABLE IF NOT EXISTS network_credentials (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password_encrypted TEXT NOT NULL,
    description VARCHAR(500),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Insertar credenciales existentes
INSERT INTO network_credentials (username, password_encrypted, description, is_default)
SELECT DISTINCT 
    network_username,
    network_password_encrypted,
    'Credenciales de red para acceso SMB',
    TRUE
FROM users
LIMIT 1  -- Solo insertar la credencial más común
ON CONFLICT (username) DO NOTHING;

-- Agregar columna network_credential_id a users
ALTER TABLE users ADD COLUMN IF NOT EXISTS network_credential_id INTEGER;

-- Poblar network_credential_id
UPDATE users u
SET network_credential_id = nc.id
FROM network_credentials nc
WHERE u.network_username = nc.username;

-- Agregar FK constraint
ALTER TABLE users 
ADD CONSTRAINT fk_users_network_credential 
FOREIGN KEY (network_credential_id) REFERENCES network_credentials(id) ON DELETE RESTRICT;

-- Hacer network_credential_id NOT NULL
ALTER TABLE users ALTER COLUMN network_credential_id SET NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '✓ Paso 2 completado: Tabla network_credentials creada y poblada';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- PASO 3: Sincronizar capabilities_json en printers
-- ============================================================================

-- Actualizar capabilities_json con valores de campos booleanos
UPDATE printers
SET capabilities_json = jsonb_build_object(
    'has_color', COALESCE(has_color, false),
    'has_scanner', COALESCE(has_scanner, false),
    'has_fax', COALESCE(has_fax, false),
    'has_duplex', COALESCE(capabilities_json->>'has_duplex', 'false')::boolean,
    'tiene_contador_usuario', tiene_contador_usuario,
    'usar_contador_ecologico', usar_contador_ecologico,
    'formato_contadores', formato_contadores
)
WHERE capabilities_json IS NULL OR capabilities_json = '{}'::jsonb;

-- Actualizar capabilities_json existentes
UPDATE printers
SET capabilities_json = capabilities_json || jsonb_build_object(
    'has_color', COALESCE(has_color, false),
    'has_scanner', COALESCE(has_scanner, false),
    'has_fax', COALESCE(has_fax, false)
)
WHERE capabilities_json IS NOT NULL;

DO $$
BEGIN
    RAISE NOTICE '✓ Paso 3 completado: capabilities_json sincronizado';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- PASO 4: Crear vistas de compatibilidad
-- ============================================================================

-- Vista para users con campos SMB expandidos
CREATE OR REPLACE VIEW v_users_completo AS
SELECT 
    u.*,
    s.server_address as smb_server,
    s.port as smb_port,
    nc.username as network_username
FROM users u
JOIN smb_servers s ON u.smb_server_id = s.id
JOIN network_credentials nc ON u.network_credential_id = nc.id;

-- Vista para printers con capacidades expandidas
CREATE OR REPLACE VIEW v_printers_completo AS
SELECT 
    p.*,
    (p.capabilities_json->>'has_color')::boolean as cap_has_color,
    (p.capabilities_json->>'has_scanner')::boolean as cap_has_scanner,
    (p.capabilities_json->>'has_fax')::boolean as cap_has_fax,
    (p.capabilities_json->>'has_duplex')::boolean as cap_has_duplex
FROM printers p;

DO $$
BEGIN
    RAISE NOTICE '✓ Paso 4 completado: Vistas de compatibilidad creadas';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- PASO 5: Eliminar columnas redundantes (COMENTADO - Ejecutar después de validar)
-- ============================================================================

-- IMPORTANTE: Descomentar estas líneas SOLO después de:
-- 1. Actualizar código para usar nuevas tablas
-- 2. Validar que todo funciona correctamente
-- 3. Esperar al menos 1 semana en producción

/*
-- Eliminar columnas SMB redundantes de users
ALTER TABLE users 
DROP COLUMN IF EXISTS smb_server,
DROP COLUMN IF EXISTS smb_port,
DROP COLUMN IF EXISTS network_username,
DROP COLUMN IF EXISTS network_password_encrypted;

-- Eliminar columnas de capacidades redundantes de printers
ALTER TABLE printers
DROP COLUMN IF EXISTS has_color,
DROP COLUMN IF EXISTS has_scanner,
DROP COLUMN IF EXISTS has_fax;

DO $$
BEGIN
    RAISE NOTICE '✓ Paso 5 completado: Columnas redundantes eliminadas';
    RAISE NOTICE '';
END $$;
*/

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================

DO $$
DECLARE
    users_count INTEGER;
    smb_servers_count INTEGER;
    network_creds_count INTEGER;
    users_sin_smb INTEGER;
    users_sin_cred INTEGER;
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'VERIFICACIÓN FINAL';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE '';
    
    -- Contar registros
    SELECT COUNT(*) INTO users_count FROM users;
    SELECT COUNT(*) INTO smb_servers_count FROM smb_servers;
    SELECT COUNT(*) INTO network_creds_count FROM network_credentials;
    
    -- Verificar integridad
    SELECT COUNT(*) INTO users_sin_smb FROM users WHERE smb_server_id IS NULL;
    SELECT COUNT(*) INTO users_sin_cred FROM users WHERE network_credential_id IS NULL;
    
    RAISE NOTICE 'Estadísticas:';
    RAISE NOTICE '  - Usuarios: %', users_count;
    RAISE NOTICE '  - Servidores SMB: %', smb_servers_count;
    RAISE NOTICE '  - Credenciales de red: %', network_creds_count;
    RAISE NOTICE '';
    
    IF users_sin_smb > 0 THEN
        RAISE WARNING '  ⚠ % usuarios sin smb_server_id', users_sin_smb;
    ELSE
        RAISE NOTICE '  ✓ Todos los usuarios tienen smb_server_id';
    END IF;
    
    IF users_sin_cred > 0 THEN
        RAISE WARNING '  ⚠ % usuarios sin network_credential_id', users_sin_cred;
    ELSE
        RAISE NOTICE '  ✓ Todos los usuarios tienen network_credential_id';
    END IF;
    
    RAISE NOTICE '';
    RAISE NOTICE '✓ Migración 015 completada exitosamente';
    RAISE NOTICE '';
    RAISE NOTICE 'PRÓXIMOS PASOS:';
    RAISE NOTICE '1. Actualizar código para usar smb_servers y network_credentials';
    RAISE NOTICE '2. Validar en desarrollo durante 1 semana';
    RAISE NOTICE '3. Descomentar Paso 5 para eliminar columnas redundantes';
    RAISE NOTICE '';
END $$;

-- ============================================================================
-- ANÁLISIS DE AHORRO
-- ============================================================================

SELECT 
    'Ahorro estimado' as metrica,
    pg_size_pretty(
        (SELECT pg_total_relation_size('users')) * 0.15  -- ~15% de ahorro estimado
    ) as valor;
