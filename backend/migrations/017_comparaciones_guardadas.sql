BEGIN;

-- 1. Tabla de comparaciones guardadas
CREATE TABLE IF NOT EXISTS comparaciones_guardadas (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    
    -- Relación con los dos cierres comparados
    cierre1_id INTEGER NOT NULL REFERENCES cierres_mensuales(id) ON DELETE CASCADE,
    cierre2_id INTEGER NOT NULL REFERENCES cierres_mensuales(id) ON DELETE CASCADE,
    
    -- Snapshot JSON liviano para listados rápidos
    snapshot_json JSONB NOT NULL,
    
    -- Campos de auditoría y multi-tenancy
    creado_por VARCHAR(100),
    admin_user_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices estratégicos para rendimiento y multi-tenancy
CREATE INDEX IF NOT EXISTS idx_comparaciones_empresa ON comparaciones_guardadas(empresa_id);
CREATE INDEX IF NOT EXISTS idx_comparaciones_cierre1 ON comparaciones_guardadas(cierre1_id);
CREATE INDEX IF NOT EXISTS idx_comparaciones_cierre2 ON comparaciones_guardadas(cierre2_id);
CREATE INDEX IF NOT EXISTS idx_comparaciones_created_at ON comparaciones_guardadas(created_at DESC);

-- 2. Índice compuesto en cierres_mensuales_usuarios para acelerar búsquedas y ordenamientos
CREATE INDEX IF NOT EXISTS idx_cierres_usuarios_cierre_consumo 
ON cierres_mensuales_usuarios(cierre_mensual_id, consumo_total DESC);

-- 3. Recreación de la función get_comparativa_periodos con datos por función detallados
CREATE OR REPLACE FUNCTION get_comparativa_periodos(
    p_fecha_inicio_a DATE,
    p_fecha_fin_a DATE,
    p_fecha_inicio_b DATE,
    p_fecha_fin_b DATE
)
RETURNS TABLE (
    indicador VARCHAR,
    periodo_a BIGINT,
    periodo_b BIGINT,
    variacion NUMERIC
) AS $$
DECLARE
    v_total_a BIGINT; v_total_b BIGINT;
    v_copiadora_a BIGINT; v_copiadora_b BIGINT;
    v_impresora_a BIGINT; v_impresora_b BIGINT;
    v_escaner_a BIGINT; v_escaner_b BIGINT;
    v_fax_a BIGINT; v_fax_b BIGINT;
BEGIN
    -- Período A
    SELECT 
        SUM(cm.total_paginas), SUM(cm.diferencia_copiadora), 
        SUM(cm.diferencia_impresora), SUM(cm.diferencia_escaner), 
        SUM(cm.diferencia_fax)
    INTO v_total_a, v_copiadora_a, v_impresora_a, v_escaner_a, v_fax_a
    FROM cierres_mensuales cm
    WHERE cm.fecha_inicio >= p_fecha_inicio_a AND cm.fecha_fin <= p_fecha_fin_a;
    
    -- Período B
    SELECT 
        SUM(cm.total_paginas), SUM(cm.diferencia_copiadora), 
        SUM(cm.diferencia_impresora), SUM(cm.diferencia_escaner), 
        SUM(cm.diferencia_fax)
    INTO v_total_b, v_copiadora_b, v_impresora_b, v_escaner_b, v_fax_b
    FROM cierres_mensuales cm
    WHERE cm.fecha_inicio >= p_fecha_inicio_b AND cm.fecha_fin <= p_fecha_fin_b;
    
    -- Filas retornadas dinámicamente
    -- Fila 1: Total
    RETURN QUERY
    SELECT 
        'Total de Páginas'::VARCHAR,
        COALESCE(v_total_a, 0), COALESCE(v_total_b, 0),
        CASE WHEN COALESCE(v_total_b, 0) > 0 THEN ROUND(((COALESCE(v_total_a, 0)::NUMERIC - v_total_b::NUMERIC) / v_total_b::NUMERIC) * 100, 2) ELSE 0 END;
        
    -- Fila 2: Copiado
    RETURN QUERY
    SELECT 
        'Páginas Copiadas'::VARCHAR,
        COALESCE(v_copiadora_a, 0), COALESCE(v_copiadora_b, 0),
        CASE WHEN COALESCE(v_copiadora_b, 0) > 0 THEN ROUND(((COALESCE(v_copiadora_a, 0)::NUMERIC - v_copiadora_b::NUMERIC) / v_copiadora_b::NUMERIC) * 100, 2) ELSE 0 END;

    -- Fila 3: Impresión
    RETURN QUERY
    SELECT 
        'Páginas Impresas'::VARCHAR,
        COALESCE(v_impresora_a, 0), COALESCE(v_impresora_b, 0),
        CASE WHEN COALESCE(v_impresora_b, 0) > 0 THEN ROUND(((COALESCE(v_impresora_a, 0)::NUMERIC - v_impresora_b::NUMERIC) / v_impresora_b::NUMERIC) * 100, 2) ELSE 0 END;

    -- Fila 4: Escáner
    RETURN QUERY
    SELECT 
        'Páginas Escaneadas'::VARCHAR,
        COALESCE(v_escaner_a, 0), COALESCE(v_escaner_b, 0),
        CASE WHEN COALESCE(v_escaner_b, 0) > 0 THEN ROUND(((COALESCE(v_escaner_a, 0)::NUMERIC - v_escaner_b::NUMERIC) / v_escaner_b::NUMERIC) * 100, 2) ELSE 0 END;

    -- Fila 5: Fax
    RETURN QUERY
    SELECT 
        'Páginas de Fax'::VARCHAR,
        COALESCE(v_fax_a, 0), COALESCE(v_fax_b, 0),
        CASE WHEN COALESCE(v_fax_b, 0) > 0 THEN ROUND(((COALESCE(v_fax_a, 0)::NUMERIC - v_fax_b::NUMERIC) / v_fax_b::NUMERIC) * 100, 2) ELSE 0 END;
END;
$$ LANGUAGE plpgsql STABLE;

COMMIT;
