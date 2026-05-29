-- Función 1: KPIs del Dashboard
CREATE OR REPLACE FUNCTION get_dashboard_kpis()
RETURNS TABLE (
    total_equipos INTEGER,
    equipos_online INTEGER,
    equipos_offline INTEGER,
    usuarios_provisionados INTEGER,
    cierres_pendientes INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_equipos,
        COUNT(*) FILTER (WHERE status = 'ONLINE')::INTEGER as equipos_online,
        COUNT(*) FILTER (WHERE status = 'OFFLINE')::INTEGER as equipos_offline,
        (SELECT COUNT(DISTINCT user_id)::INTEGER 
         FROM user_printer_assignments 
         WHERE is_active = true) as usuarios_provisionados,
        (SELECT COUNT(*)::INTEGER
         FROM printers p
         WHERE NOT EXISTS (
             SELECT 1 FROM cierres_mensuales cm
             WHERE cm.printer_id = p.id
             AND cm.anio = EXTRACT(YEAR FROM CURRENT_DATE)
             AND cm.mes = EXTRACT(MONTH FROM CURRENT_DATE)
         )) as cierres_pendientes
    FROM printers;
END;
$$ LANGUAGE plpgsql STABLE;

-- Función 2: Top Impresoras
CREATE OR REPLACE FUNCTION get_top_impresoras(
    p_fecha_inicio DATE,
    p_fecha_fin DATE,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    printer_id INTEGER,
    hostname VARCHAR,
    modelo VARCHAR,
    ubicacion VARCHAR,
    total_paginas BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.hostname,
        p.detected_model,
        p.location,
        SUM(cm.total_paginas)::BIGINT
    FROM printers p
    INNER JOIN cierres_mensuales cm ON p.id = cm.printer_id
    WHERE cm.fecha_inicio >= p_fecha_inicio
      AND cm.fecha_fin <= p_fecha_fin
    GROUP BY p.id, p.hostname, p.detected_model, p.location
    ORDER BY SUM(cm.total_paginas) DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Función 3: Evolución de Consumo
CREATE OR REPLACE FUNCTION get_evolucion_consumo(
    p_meses INTEGER DEFAULT 12
)
RETURNS TABLE (
    anio INTEGER,
    mes INTEGER,
    mes_nombre VARCHAR,
    total_paginas BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        cm.anio,
        cm.mes,
        TO_CHAR(TO_DATE(cm.anio || '-' || cm.mes || '-01', 'YYYY-MM-DD'), 'Mon')::VARCHAR,
        SUM(cm.total_paginas)::BIGINT
    FROM cierres_mensuales cm
    WHERE TO_DATE(cm.anio || '-' || cm.mes || '-01', 'YYYY-MM-DD') >= CURRENT_DATE - (p_meses || ' months')::INTERVAL
    GROUP BY cm.anio, cm.mes
    ORDER BY cm.anio DESC, cm.mes DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- Función 4: Comparativa entre Períodos
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
    v_total_a BIGINT;
    v_total_b BIGINT;
BEGIN
    SELECT SUM(cm.total_paginas)
    INTO v_total_a
    FROM cierres_mensuales cm
    WHERE cm.fecha_inicio >= p_fecha_inicio_a
      AND cm.fecha_fin <= p_fecha_fin_a;
    
    SELECT SUM(cm.total_paginas)
    INTO v_total_b
    FROM cierres_mensuales cm
    WHERE cm.fecha_inicio >= p_fecha_inicio_b
      AND cm.fecha_fin <= p_fecha_fin_b;
    
    RETURN QUERY
    SELECT 
        'Total de Páginas'::VARCHAR,
        COALESCE(v_total_a, 0),
        COALESCE(v_total_b, 0),
        CASE 
            WHEN v_total_b > 0 THEN ROUND(((v_total_a::NUMERIC - v_total_b::NUMERIC) / v_total_b::NUMERIC) * 100, 2)
            ELSE 0
        END;
END;
$$ LANGUAGE plpgsql STABLE;
