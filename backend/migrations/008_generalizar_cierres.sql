-- ============================================================================
-- MIGRACIÓN 008: Generalizar Sistema de Cierres
-- ============================================================================
-- Descripción: Convierte el sistema de "cierres mensuales" a un sistema
--              unificado que soporta cierres de cualquier período
--              (diario, semanal, mensual, personalizado)
--
-- Cambios:
-- 1. Renombrar tablas para ser más genéricas
-- 2. Agregar campos para períodos flexibles
-- 3. Actualizar constraints y validaciones
-- 4. Mantener compatibilidad con datos existentes
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. AGREGAR NUEVOS CAMPOS A TABLA EXISTENTE
-- ============================================================================

-- Tipo de período
ALTER TABLE cierres_mensuales 
ADD COLUMN tipo_periodo VARCHAR(20) DEFAULT 'mensual' 
CHECK (tipo_periodo IN ('diario', 'semanal', 'mensual', 'personalizado'));

COMMENT ON COLUMN cierres_mensuales.tipo_periodo IS 
'Tipo de período del cierre: diario, semanal, mensual, personalizado';

-- Fecha de inicio del período
ALTER TABLE cierres_mensuales 
ADD COLUMN fecha_inicio DATE;

COMMENT ON COLUMN cierres_mensuales.fecha_inicio IS 
'Fecha de inicio del período del cierre';

-- Fecha de fin del período
ALTER TABLE cierres_mensuales 
ADD COLUMN fecha_fin DATE;

COMMENT ON COLUMN cierres_mensuales.fecha_fin IS 
'Fecha de fin del período del cierre';

-- ============================================================================
-- 2. MIGRAR DATOS EXISTENTES
-- ============================================================================

-- Calcular fecha_inicio y fecha_fin para cierres mensuales existentes
UPDATE cierres_mensuales
SET 
    fecha_inicio = DATE(CONCAT(anio, '-', LPAD(mes::TEXT, 2, '0'), '-01')),
    fecha_fin = (DATE(CONCAT(anio, '-', LPAD(mes::TEXT, 2, '0'), '-01')) + INTERVAL '1 month' - INTERVAL '1 day')::DATE,
    tipo_periodo = 'mensual'
WHERE fecha_inicio IS NULL;

-- ============================================================================
-- 3. HACER CAMPOS OBLIGATORIOS
-- ============================================================================

ALTER TABLE cierres_mensuales 
ALTER COLUMN fecha_inicio SET NOT NULL;

ALTER TABLE cierres_mensuales 
ALTER COLUMN fecha_fin SET NOT NULL;

ALTER TABLE cierres_mensuales 
ALTER COLUMN tipo_periodo SET NOT NULL;

-- ============================================================================
-- 4. AGREGAR VALIDACIONES
-- ============================================================================

-- Validar que fecha_fin >= fecha_inicio
ALTER TABLE cierres_mensuales
ADD CONSTRAINT check_fecha_fin_mayor_igual_inicio
CHECK (fecha_fin >= fecha_inicio);

-- Validar que el período no sea muy largo (máximo 1 año)
ALTER TABLE cierres_mensuales
ADD CONSTRAINT check_periodo_maximo_1_anio
CHECK (fecha_fin - fecha_inicio <= 365);

-- Validar consistencia de fechas con año/mes para cierres mensuales
ALTER TABLE cierres_mensuales
ADD CONSTRAINT check_consistencia_mensual
CHECK (
    tipo_periodo != 'mensual' OR (
        EXTRACT(YEAR FROM fecha_inicio) = anio AND
        EXTRACT(MONTH FROM fecha_inicio) = mes AND
        fecha_inicio = DATE_TRUNC('month', fecha_inicio)::DATE AND
        fecha_fin = (DATE_TRUNC('month', fecha_inicio) + INTERVAL '1 month' - INTERVAL '1 day')::DATE
    )
);

-- ============================================================================
-- 5. ACTUALIZAR ÍNDICES
-- ============================================================================

-- Índice para búsqueda por período
CREATE INDEX idx_cierres_periodo 
ON cierres_mensuales(printer_id, fecha_inicio, fecha_fin);

-- Índice para búsqueda por tipo
CREATE INDEX idx_cierres_tipo 
ON cierres_mensuales(printer_id, tipo_periodo, fecha_inicio DESC);

-- Índice para detectar solapamientos de períodos
CREATE INDEX idx_cierres_solapamiento 
ON cierres_mensuales(printer_id, fecha_inicio, fecha_fin)
WHERE tipo_periodo IN ('diario', 'semanal', 'personalizado');

-- ============================================================================
-- 6. AGREGAR CONSTRAINT DE NO SOLAPAMIENTO
-- ============================================================================

-- Función para verificar que no haya solapamiento de períodos
CREATE OR REPLACE FUNCTION check_no_solapamiento_cierres()
RETURNS TRIGGER AS $$
BEGIN
    -- Verificar si existe un cierre que solape con el nuevo período
    IF EXISTS (
        SELECT 1 
        FROM cierres_mensuales
        WHERE printer_id = NEW.printer_id
          AND id != COALESCE(NEW.id, -1)
          AND (
              -- El nuevo período está dentro de un período existente
              (NEW.fecha_inicio >= fecha_inicio AND NEW.fecha_inicio <= fecha_fin) OR
              (NEW.fecha_fin >= fecha_inicio AND NEW.fecha_fin <= fecha_fin) OR
              -- El nuevo período contiene un período existente
              (NEW.fecha_inicio <= fecha_inicio AND NEW.fecha_fin >= fecha_fin)
          )
    ) THEN
        RAISE EXCEPTION 'Ya existe un cierre que solapa con el período % a %', 
            NEW.fecha_inicio, NEW.fecha_fin;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar no solapamiento
DROP TRIGGER IF EXISTS trigger_check_no_solapamiento_cierres ON cierres_mensuales;
CREATE TRIGGER trigger_check_no_solapamiento_cierres
    BEFORE INSERT OR UPDATE ON cierres_mensuales
    FOR EACH ROW
    EXECUTE FUNCTION check_no_solapamiento_cierres();

-- ============================================================================
-- 7. RENOMBRAR TABLAS (Opcional - comentado por compatibilidad)
-- ============================================================================

-- Si quieres renombrar las tablas para que sean más genéricas:
-- ALTER TABLE cierres_mensuales RENAME TO cierres;
-- ALTER TABLE cierres_mensuales_usuarios RENAME TO cierres_usuarios;
-- 
-- Por ahora las dejamos con el nombre actual para mantener compatibilidad

-- ============================================================================
-- 8. ACTUALIZAR COMENTARIOS
-- ============================================================================

COMMENT ON TABLE cierres_mensuales IS 
'Tabla de cierres de contadores. Soporta cierres diarios, semanales, mensuales y personalizados. 
Cada cierre guarda un snapshot inmutable de los contadores al momento del cierre.';

-- ============================================================================
-- 9. CREAR VISTA PARA FACILITAR CONSULTAS
-- ============================================================================

CREATE OR REPLACE VIEW v_cierres_resumen AS
SELECT 
    c.id,
    c.printer_id,
    p.hostname,
    p.ip_address,
    c.tipo_periodo,
    c.fecha_inicio,
    c.fecha_fin,
    c.anio,
    c.mes,
    (c.fecha_fin - c.fecha_inicio + 1) as dias_periodo,
    c.total_paginas,
    c.diferencia_total,
    c.fecha_cierre,
    c.cerrado_por,
    c.hash_verificacion,
    COUNT(cu.id) as total_usuarios,
    SUM(cu.consumo_total) as suma_consumos_usuarios,
    CASE 
        WHEN c.diferencia_total > 0 THEN 
            ABS(SUM(cu.consumo_total) - c.diferencia_total) / c.diferencia_total * 100
        ELSE 0
    END as porcentaje_diferencia
FROM cierres_mensuales c
LEFT JOIN printers p ON c.printer_id = p.id
LEFT JOIN cierres_mensuales_usuarios cu ON c.id = cu.cierre_mensual_id
GROUP BY c.id, p.hostname, p.ip_address;

COMMENT ON VIEW v_cierres_resumen IS 
'Vista resumen de cierres con información agregada de usuarios y validación de integridad';

-- ============================================================================
-- 10. FUNCIÓN AUXILIAR PARA OBTENER ÚLTIMO CIERRE
-- ============================================================================

CREATE OR REPLACE FUNCTION get_ultimo_cierre(p_printer_id INTEGER, p_fecha DATE)
RETURNS TABLE (
    id INTEGER,
    fecha_inicio DATE,
    fecha_fin DATE,
    total_paginas INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.fecha_inicio,
        c.fecha_fin,
        c.total_paginas
    FROM cierres_mensuales c
    WHERE c.printer_id = p_printer_id
      AND c.fecha_fin < p_fecha
    ORDER BY c.fecha_fin DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_ultimo_cierre IS 
'Obtiene el último cierre anterior a una fecha dada';

-- ============================================================================
-- VERIFICACIÓN FINAL
-- ============================================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    -- Verificar que todos los registros tienen fechas
    SELECT COUNT(*) INTO v_count
    FROM cierres_mensuales
    WHERE fecha_inicio IS NULL OR fecha_fin IS NULL;
    
    IF v_count > 0 THEN
        RAISE EXCEPTION 'Hay % registros sin fechas de período', v_count;
    END IF;
    
    -- Verificar consistencia de fechas
    SELECT COUNT(*) INTO v_count
    FROM cierres_mensuales
    WHERE fecha_fin < fecha_inicio;
    
    IF v_count > 0 THEN
        RAISE EXCEPTION 'Hay % registros con fecha_fin < fecha_inicio', v_count;
    END IF;
    
    RAISE NOTICE '✅ Migración 008 completada exitosamente';
    RAISE NOTICE '   - Campos agregados: tipo_periodo, fecha_inicio, fecha_fin';
    RAISE NOTICE '   - Datos migrados: % registros', (SELECT COUNT(*) FROM cierres_mensuales);
    RAISE NOTICE '   - Constraints agregados: 3';
    RAISE NOTICE '   - Índices agregados: 3';
    RAISE NOTICE '   - Trigger agregado: check_no_solapamiento_cierres';
    RAISE NOTICE '   - Vista creada: v_cierres_resumen';
    RAISE NOTICE '   - Función creada: get_ultimo_cierre';
END $$;

COMMIT;
