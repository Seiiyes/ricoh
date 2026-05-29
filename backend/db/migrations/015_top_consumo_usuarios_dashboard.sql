-- Ranking de consumo por usuario de Ricoh (suma consumo_total en cierres del período)
CREATE OR REPLACE FUNCTION get_top_consumo_usuarios(
    p_fecha_inicio DATE,
    p_fecha_fin DATE,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    user_id INTEGER,
    nombre VARCHAR,
    codigo_usuario VARCHAR,
    total_consumo_paginas BIGINT,
    cierres_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.name::VARCHAR,
        u.codigo_de_usuario::VARCHAR,
        SUM(cmu.consumo_total)::BIGINT AS total_consumo_paginas,
        COUNT(*)::INTEGER AS cierres_count
    FROM cierres_mensuales_usuarios cmu
    INNER JOIN cierres_mensuales cm ON cm.id = cmu.cierre_mensual_id
    INNER JOIN users u ON u.id = cmu.user_id
    WHERE cm.fecha_inicio >= p_fecha_inicio
      AND cm.fecha_fin <= p_fecha_fin
    GROUP BY u.id, u.name, u.codigo_de_usuario
    ORDER BY total_consumo_paginas DESC NULLS LAST
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;
