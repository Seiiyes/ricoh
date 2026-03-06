-- Migration 007: Add snapshot table and fix critical database issues
-- Date: 2026-03-03
-- Description: Adds cierres_mensuales_usuarios table and fixes integrity, validation, and performance issues
-- Author: System Architect
-- Estimated time: 2-5 minutes

-- ============================================================================
-- PARTE 1: CREAR TABLA DE SNAPSHOT DE USUARIOS EN CIERRES
-- ============================================================================

CREATE TABLE IF NOT EXISTS cierres_mensuales_usuarios (
    id SERIAL PRIMARY KEY,
    cierre_mensual_id INTEGER NOT NULL REFERENCES cierres_mensuales(id) ON DELETE CASCADE,
    
    -- Usuario
    codigo_usuario VARCHAR(8) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    
    -- Contadores al cierre (snapshot inmutable)
    total_paginas INTEGER NOT NULL CHECK (total_paginas >= 0),
    total_bn INTEGER NOT NULL CHECK (total_bn >= 0),
    total_color INTEGER NOT NULL CHECK (total_color >= 0),
    
    -- Desglose por función
    copiadora_bn INTEGER NOT NULL CHECK (copiadora_bn >= 0),
    copiadora_color INTEGER NOT NULL CHECK (copiadora_color >= 0),
    impresora_bn INTEGER NOT NULL CHECK (impresora_bn >= 0),
    impresora_color INTEGER NOT NULL CHECK (impresora_color >= 0),
    escaner_bn INTEGER NOT NULL CHECK (escaner_bn >= 0),
    escaner_color INTEGER NOT NULL CHECK (escaner_color >= 0),
    fax_bn INTEGER NOT NULL CHECK (fax_bn >= 0),
    
    -- Consumo del mes (diferencia con mes anterior)
    -- Puede ser negativo si hubo reset de contador
    consumo_total INTEGER NOT NULL,
    consumo_copiadora INTEGER NOT NULL,
    consumo_impresora INTEGER NOT NULL,
    consumo_escaner INTEGER NOT NULL,
    consumo_fax INTEGER NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Constraints
    CONSTRAINT uk_cierre_usuario UNIQUE(cierre_mensual_id, codigo_usuario)
);

-- Índices para snapshot (optimización de queries)
CREATE INDEX idx_cierres_usuarios_cierre ON cierres_mensuales_usuarios(cierre_mensual_id);
CREATE INDEX idx_cierres_usuarios_codigo ON cierres_mensuales_usuarios(codigo_usuario);
CREATE INDEX idx_cierres_usuarios_consumo ON cierres_mensuales_usuarios(consumo_total DESC);

-- Comentarios para documentación
COMMENT ON TABLE cierres_mensuales_usuarios IS 'Snapshot inmutable de contadores por usuario al momento del cierre mensual. Permite auditoría y facturación sin depender de datos históricos.';
COMMENT ON COLUMN cierres_mensuales_usuarios.cierre_mensual_id IS 'Referencia al cierre mensual padre';
COMMENT ON COLUMN cierres_mensuales_usuarios.consumo_total IS 'Consumo del mes (diferencia con mes anterior). Puede ser negativo si hubo reset de contador.';
COMMENT ON COLUMN cierres_mensuales_usuarios.total_paginas IS 'Total acumulado de páginas al momento del cierre';

-- ============================================================================
-- PARTE 2: AGREGAR CONSTRAINTS DE VALIDACIÓN
-- ============================================================================

-- Validar mes (1-12)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_mes_valido' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales 
        ADD CONSTRAINT chk_mes_valido CHECK (mes BETWEEN 1 AND 12);
    END IF;
END $$;

-- Validar año (2020-2100)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_anio_valido' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales 
        ADD CONSTRAINT chk_anio_valido CHECK (anio BETWEEN 2020 AND 2100);
    END IF;
END $$;

-- Validar contadores de cierre no negativos
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_total_paginas_positivo' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales
        ADD CONSTRAINT chk_total_paginas_positivo CHECK (total_paginas >= 0);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_total_copiadora_positivo' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales
        ADD CONSTRAINT chk_total_copiadora_positivo CHECK (total_copiadora >= 0);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_total_impresora_positivo' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales
        ADD CONSTRAINT chk_total_impresora_positivo CHECK (total_impresora >= 0);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_total_escaner_positivo' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales
        ADD CONSTRAINT chk_total_escaner_positivo CHECK (total_escaner >= 0);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_total_fax_positivo' 
        AND table_name = 'cierres_mensuales'
    ) THEN
        ALTER TABLE cierres_mensuales
        ADD CONSTRAINT chk_total_fax_positivo CHECK (total_fax >= 0);
    END IF;
END $$;

-- Validar contadores de usuario no negativos
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_usuario_total_positivo' 
        AND table_name = 'contadores_usuario'
    ) THEN
        ALTER TABLE contadores_usuario
        ADD CONSTRAINT chk_usuario_total_positivo CHECK (total_paginas >= 0);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_usuario_bn_positivo' 
        AND table_name = 'contadores_usuario'
    ) THEN
        ALTER TABLE contadores_usuario
        ADD CONSTRAINT chk_usuario_bn_positivo CHECK (total_bn >= 0);
    END IF;
END $$;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_usuario_color_positivo' 
        AND table_name = 'contadores_usuario'
    ) THEN
        ALTER TABLE contadores_usuario
        ADD CONSTRAINT chk_usuario_color_positivo CHECK (total_color >= 0);
    END IF;
END $$;

-- Validar contadores de impresora no negativos
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'chk_impresora_total_positivo' 
        AND table_name = 'contadores_impresora'
    ) THEN
        ALTER TABLE contadores_impresora
        ADD CONSTRAINT chk_impresora_total_positivo CHECK (total >= 0);
    END IF;
END $$;

-- ============================================================================
-- PARTE 3: AGREGAR ÍNDICES COMPUESTOS PARA OPTIMIZACIÓN
-- ============================================================================

-- Índice para query de última lectura por usuario (query más frecuente)
CREATE INDEX IF NOT EXISTS idx_contadores_usuario_lookup 
ON contadores_usuario(printer_id, codigo_usuario, created_at DESC);

-- Índice para query de cierre mensual
CREATE INDEX IF NOT EXISTS idx_contadores_usuario_cierre 
ON contadores_usuario(printer_id, created_at DESC);

-- Índice parcial para usuarios activos (solo usuarios con actividad)
CREATE INDEX IF NOT EXISTS idx_contadores_usuario_activos 
ON contadores_usuario(printer_id, total_paginas)
WHERE total_paginas > 0;

-- Índice para query de impresora por fecha
CREATE INDEX IF NOT EXISTS idx_contadores_impresora_fecha
ON contadores_impresora(printer_id, created_at DESC);

-- ============================================================================
-- PARTE 4: ELIMINAR ÍNDICES DUPLICADOS
-- ============================================================================

-- SQLAlchemy crea índices automáticamente con prefijo ix_
-- Las migraciones crean índices con prefijo idx_
-- Eliminamos los ix_* porque los idx_* son más descriptivos

DROP INDEX IF EXISTS ix_cierres_mensuales_anio;
DROP INDEX IF EXISTS ix_cierres_mensuales_mes;
DROP INDEX IF EXISTS ix_cierres_mensuales_printer_id;
DROP INDEX IF EXISTS ix_cierres_mensuales_id;

DROP INDEX IF EXISTS ix_contadores_usuario_codigo_usuario;
DROP INDEX IF EXISTS ix_contadores_usuario_fecha_lectura;
DROP INDEX IF EXISTS ix_contadores_usuario_printer_id;
DROP INDEX IF EXISTS ix_contadores_usuario_id;

DROP INDEX IF EXISTS ix_contadores_impresora_fecha_lectura;
DROP INDEX IF EXISTS ix_contadores_impresora_printer_id;
DROP INDEX IF EXISTS ix_contadores_impresora_id;

-- Los índices idx_* de las migraciones anteriores son suficientes

-- ============================================================================
-- PARTE 5: AGREGAR COLUMNAS DE AUDITORÍA
-- ============================================================================

-- Auditoría en cierres_mensuales
ALTER TABLE cierres_mensuales
ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE cierres_mensuales
ADD COLUMN IF NOT EXISTS modified_by VARCHAR(100);

ALTER TABLE cierres_mensuales
ADD COLUMN IF NOT EXISTS hash_verificacion VARCHAR(64);

-- Comentarios para auditoría
COMMENT ON COLUMN cierres_mensuales.modified_at IS 'Fecha de última modificación del cierre (si aplica)';
COMMENT ON COLUMN cierres_mensuales.modified_by IS 'Usuario que modificó el cierre (si aplica)';
COMMENT ON COLUMN cierres_mensuales.hash_verificacion IS 'SHA256 hash para verificar integridad del cierre';

-- ============================================================================
-- PARTE 6: AGREGAR COMENTARIOS FALTANTES PARA DOCUMENTACIÓN
-- ============================================================================

-- Comentarios en users
COMMENT ON TABLE users IS 'Usuarios del sistema para aprovisionamiento en impresoras Ricoh';
COMMENT ON COLUMN users.codigo_de_usuario IS 'Código de usuario de 8 dígitos para autenticación en impresora';
COMMENT ON COLUMN users.empresa IS 'Empresa a la que pertenece el usuario (para facturación)';
COMMENT ON COLUMN users.centro_costos IS 'Centro de costos para facturación y reportes';
COMMENT ON COLUMN users.network_username IS 'Usuario de red para autenticación de carpeta SMB';
COMMENT ON COLUMN users.smb_path IS 'Ruta completa de carpeta SMB para escaneo';

-- Comentarios en printers
COMMENT ON TABLE printers IS 'Impresoras Ricoh registradas en el sistema';
COMMENT ON COLUMN printers.tiene_contador_usuario IS 'Indica si la impresora tiene getUserCounter.cgi disponible';
COMMENT ON COLUMN printers.usar_contador_ecologico IS 'Indica si se debe usar getEcoCounter.cgi para contadores de usuario (impresoras B/N)';
COMMENT ON COLUMN printers.empresa IS 'Empresa a la que pertenece la impresora';
COMMENT ON COLUMN printers.serial_number IS 'Número de serie de la impresora (puede ser NULL)';

-- Comentarios en contadores_usuario
COMMENT ON COLUMN contadores_usuario.tipo_contador IS 'Tipo de contador: "usuario" (getUserCounter) o "ecologico" (getEcoCounter)';
COMMENT ON COLUMN contadores_usuario.created_at IS 'Timestamp de cuando se guardó el registro (agrupa lecturas de una sesión)';
COMMENT ON COLUMN contadores_usuario.fecha_lectura IS 'Timestamp de cuando se leyó el contador de la impresora';

-- Comentarios en contadores_impresora
COMMENT ON COLUMN contadores_impresora.created_at IS 'Timestamp de cuando se guardó el registro';
COMMENT ON COLUMN contadores_impresora.fecha_lectura IS 'Timestamp de cuando se leyó el contador de la impresora';

-- Comentarios en cierres_mensuales
COMMENT ON COLUMN cierres_mensuales.diferencia_total IS 'Consumo del mes (diferencia con mes anterior)';
COMMENT ON COLUMN cierres_mensuales.cerrado_por IS 'Usuario que realizó el cierre mensual';
COMMENT ON COLUMN cierres_mensuales.notas IS 'Notas adicionales sobre el cierre (incidencias, observaciones)';

-- ============================================================================
-- PARTE 7: VERIFICACIÓN DE MIGRACIÓN
-- ============================================================================

-- Verificar que la tabla se creó correctamente
DO $$
DECLARE
    tabla_existe INTEGER;
    indices_count INTEGER;
    constraints_count INTEGER;
BEGIN
    -- Verificar tabla
    SELECT COUNT(*) INTO tabla_existe
    FROM information_schema.tables
    WHERE table_name = 'cierres_mensuales_usuarios';
    
    IF tabla_existe = 0 THEN
        RAISE EXCEPTION 'ERROR: Tabla cierres_mensuales_usuarios no se creó';
    END IF;
    
    -- Verificar índices
    SELECT COUNT(*) INTO indices_count
    FROM pg_indexes
    WHERE tablename = 'cierres_mensuales_usuarios';
    
    IF indices_count < 3 THEN
        RAISE WARNING 'ADVERTENCIA: Se esperaban al menos 3 índices en cierres_mensuales_usuarios, se encontraron %', indices_count;
    END IF;
    
    -- Verificar constraints
    SELECT COUNT(*) INTO constraints_count
    FROM information_schema.table_constraints
    WHERE table_name = 'cierres_mensuales_usuarios'
    AND constraint_type = 'CHECK';
    
    IF constraints_count < 10 THEN
        RAISE WARNING 'ADVERTENCIA: Se esperaban al menos 10 CHECK constraints en cierres_mensuales_usuarios, se encontraron %', constraints_count;
    END IF;
    
    RAISE NOTICE '✅ Migración 007 completada exitosamente';
    RAISE NOTICE '   - Tabla cierres_mensuales_usuarios creada';
    RAISE NOTICE '   - % índices creados', indices_count;
    RAISE NOTICE '   - % CHECK constraints agregados', constraints_count;
END $$;

-- Mostrar resumen de cambios
SELECT 
    'Tablas creadas' as tipo,
    COUNT(*) as cantidad
FROM information_schema.tables
WHERE table_name = 'cierres_mensuales_usuarios'

UNION ALL

SELECT 
    'Índices compuestos agregados' as tipo,
    COUNT(*) as cantidad
FROM pg_indexes
WHERE indexname LIKE 'idx_contadores_usuario_%'
AND tablename = 'contadores_usuario'

UNION ALL

SELECT 
    'CHECK constraints agregados' as tipo,
    COUNT(*) as cantidad
FROM information_schema.table_constraints
WHERE constraint_type = 'CHECK'
AND table_name IN ('cierres_mensuales', 'contadores_usuario', 'contadores_impresora', 'cierres_mensuales_usuarios')

UNION ALL

SELECT 
    'Columnas de auditoría agregadas' as tipo,
    COUNT(*) as cantidad
FROM information_schema.columns
WHERE table_name = 'cierres_mensuales'
AND column_name IN ('modified_at', 'modified_by', 'hash_verificacion');

-- ============================================================================
-- FIN DE MIGRACIÓN 007
-- ============================================================================
