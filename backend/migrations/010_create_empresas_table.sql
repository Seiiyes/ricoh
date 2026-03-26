-- ============================================================================
-- MIGRACIÓN 010: Crear Tabla Empresas y Normalizar Datos
-- ============================================================================
-- Descripción: Normaliza los campos VARCHAR de empresa en una tabla dedicada
--              con integridad referencial
--
-- Cambios:
-- 1. Crear tabla empresas con todos los campos
-- 2. Insertar empresas únicas desde printers.empresa y users.empresa
-- 3. Agregar empresa_id a printers y users
-- 4. Actualizar empresa_id con valores correspondientes
-- 5. Eliminar columnas VARCHAR antiguas
-- ============================================================================

BEGIN;

-- ============================================================================
-- PASO 0: Crear función update_updated_at_column si no existe
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ============================================================================
-- PASO 1: Crear tabla empresas
-- ============================================================================

-- Eliminar tabla si existe (solo para desarrollo, comentar en producción)
DROP TABLE IF EXISTS empresas CASCADE;

CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    razon_social VARCHAR(255) NOT NULL UNIQUE,
    nombre_comercial VARCHAR(50) NOT NULL UNIQUE,
    nit VARCHAR(20) UNIQUE,
    direccion TEXT,
    telefono VARCHAR(50),
    email VARCHAR(255),
    contacto_nombre VARCHAR(255),
    contacto_cargo VARCHAR(100),
    logo_url VARCHAR(500),
    config_json JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT chk_razon_social_no_vacia CHECK (LENGTH(TRIM(razon_social)) > 0),
    CONSTRAINT chk_nombre_comercial_formato CHECK (nombre_comercial ~ '^[a-z0-9-]+$'),
    CONSTRAINT chk_email_formato CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Índices para empresas
CREATE INDEX idx_empresas_razon_social ON empresas(razon_social);
CREATE INDEX idx_empresas_nombre_comercial ON empresas(nombre_comercial);
CREATE INDEX idx_empresas_active ON empresas(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_empresas_config ON empresas USING gin(config_json);

-- Trigger para updated_at
CREATE TRIGGER update_empresas_updated_at 
BEFORE UPDATE ON empresas
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentarios
COMMENT ON TABLE empresas IS 'Empresas/organizaciones del sistema (tenants)';
COMMENT ON COLUMN empresas.razon_social IS 'Razón social legal de la empresa';
COMMENT ON COLUMN empresas.nombre_comercial IS 'Identificador único en formato kebab-case para URLs';
COMMENT ON COLUMN empresas.nit IS 'Número de Identificación Tributaria (NIT)';
COMMENT ON COLUMN empresas.config_json IS 'Configuración: max_usuarios, max_impresoras, modulos_habilitados, etc.';

-- ============================================================================
-- PASO 2: Insertar empresas únicas desde datos existentes
-- ============================================================================

-- Función auxiliar para convertir texto a kebab-case
CREATE OR REPLACE FUNCTION to_kebab_case(text_input TEXT) RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                REGEXP_REPLACE(TRIM(text_input), '[^a-zA-Z0-9\s-]', '', 'g'),
                '\s+', '-', 'g'
            ),
            '-+', '-', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Insertar empresas únicas desde printers y users (solo si columna empresa existe)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'printers' AND column_name = 'empresa'
    ) THEN
        INSERT INTO empresas (razon_social, nombre_comercial)
        SELECT DISTINCT
            COALESCE(NULLIF(TRIM(empresa), ''), 'Sin Asignar') as razon_social,
            to_kebab_case(COALESCE(NULLIF(TRIM(empresa), ''), 'sin-asignar')) as nombre_comercial
        FROM (
            SELECT empresa FROM printers WHERE empresa IS NOT NULL
            UNION
            SELECT empresa FROM users WHERE empresa IS NOT NULL
        ) AS empresas_existentes
        ON CONFLICT (razon_social) DO NOTHING;
    END IF;
END $$;

-- Asegurar que existe empresa 'Sin Asignar' para valores NULL
INSERT INTO empresas (razon_social, nombre_comercial)
VALUES ('Sin Asignar', 'sin-asignar')
ON CONFLICT (razon_social) DO NOTHING;

-- ============================================================================
-- PASO 3: Agregar empresa_id a printers
-- ============================================================================

DO $$
BEGIN
    -- Agregar columna empresa_id si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'printers' AND column_name = 'empresa_id'
    ) THEN
        ALTER TABLE printers ADD COLUMN empresa_id INTEGER;
    END IF;
    
    -- Actualizar empresa_id si columna empresa existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'printers' AND column_name = 'empresa'
    ) THEN
        UPDATE printers p
        SET empresa_id = e.id
        FROM empresas e
        WHERE COALESCE(NULLIF(TRIM(p.empresa), ''), 'Sin Asignar') = e.razon_social;
    ELSE
        -- Si no existe columna empresa, asignar a 'Sin Asignar'
        UPDATE printers p
        SET empresa_id = e.id
        FROM empresas e
        WHERE e.nombre_comercial = 'sin-asignar' AND p.empresa_id IS NULL;
    END IF;
    
    -- Hacer empresa_id NOT NULL
    ALTER TABLE printers ALTER COLUMN empresa_id SET NOT NULL;
    
    -- Agregar foreign key constraint si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_printers_empresa'
    ) THEN
        ALTER TABLE printers
        ADD CONSTRAINT fk_printers_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE RESTRICT;
    END IF;
END $$;

-- Crear índice si no existe
CREATE INDEX IF NOT EXISTS idx_printers_empresa_id ON printers(empresa_id);

-- Eliminar columna empresa antigua si existe
ALTER TABLE printers DROP COLUMN IF EXISTS empresa;

-- ============================================================================
-- PASO 4: Agregar empresa_id a users
-- ============================================================================

DO $$
BEGIN
    -- Agregar columna empresa_id si no existe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'empresa_id'
    ) THEN
        ALTER TABLE users ADD COLUMN empresa_id INTEGER;
    END IF;
    
    -- Actualizar empresa_id si columna empresa existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'empresa'
    ) THEN
        UPDATE users u
        SET empresa_id = e.id
        FROM empresas e
        WHERE u.empresa IS NOT NULL
          AND NULLIF(TRIM(u.empresa), '') IS NOT NULL
          AND COALESCE(NULLIF(TRIM(u.empresa), ''), 'Sin Asignar') = e.razon_social;
    END IF;
    
    -- Agregar foreign key constraint si no existe (permite NULL)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_users_empresa'
    ) THEN
        ALTER TABLE users
        ADD CONSTRAINT fk_users_empresa
        FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE RESTRICT;
    END IF;
END $$;

-- Crear índice si no existe
CREATE INDEX IF NOT EXISTS idx_users_empresa_id ON users(empresa_id);

-- Eliminar columna empresa antigua si existe
ALTER TABLE users DROP COLUMN IF EXISTS empresa;

-- ============================================================================
-- PASO 5: Limpiar función auxiliar
-- ============================================================================

DROP FUNCTION to_kebab_case(TEXT);

COMMIT;

-- ============================================================================
-- Verificación
-- ============================================================================

DO $$
DECLARE
    total_empresas INTEGER;
    total_printers_con_empresa INTEGER;
    total_users_con_empresa INTEGER;
    rec RECORD;
BEGIN
    SELECT COUNT(*) INTO total_empresas FROM empresas;
    SELECT COUNT(*) INTO total_printers_con_empresa FROM printers WHERE empresa_id IS NOT NULL;
    SELECT COUNT(*) INTO total_users_con_empresa FROM users WHERE empresa_id IS NOT NULL;
    
    RAISE NOTICE '✅ Migración 010 completada exitosamente';
    RAISE NOTICE '   - Empresas creadas: %', total_empresas;
    RAISE NOTICE '   - Printers con empresa_id: %', total_printers_con_empresa;
    RAISE NOTICE '   - Users con empresa_id: %', total_users_con_empresa;
    RAISE NOTICE '';
    RAISE NOTICE '📊 Empresas en el sistema:';
    
    FOR rec IN 
        SELECT id, razon_social, nombre_comercial 
        FROM empresas 
        ORDER BY id
    LOOP
        RAISE NOTICE '   [%] % (slug: %)', rec.id, rec.razon_social, rec.nombre_comercial;
    END LOOP;
END $$;
