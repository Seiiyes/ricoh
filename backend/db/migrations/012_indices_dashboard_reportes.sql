-- Dashboard
CREATE INDEX IF NOT EXISTS idx_printers_status 
    ON printers(status) WHERE status IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_printers_empresa_status 
    ON printers(empresa_id, status);

CREATE INDEX IF NOT EXISTS idx_user_assignments_active 
    ON user_printer_assignments(user_id, is_active) 
    WHERE is_active = true;

-- Reportes
CREATE INDEX IF NOT EXISTS idx_cierres_periodo 
    ON cierres_mensuales(anio DESC, mes DESC);

CREATE INDEX IF NOT EXISTS idx_cierres_printer_periodo 
    ON cierres_mensuales(printer_id, anio DESC, mes DESC);

CREATE INDEX IF NOT EXISTS idx_cierres_fecha_rango 
    ON cierres_mensuales(fecha_inicio, fecha_fin);

-- Agregaciones de usuarios
CREATE INDEX IF NOT EXISTS idx_cierres_usuarios_cierre 
    ON cierres_mensuales_usuarios(cierre_mensual_id);

CREATE INDEX IF NOT EXISTS idx_cierres_usuarios_user 
    ON cierres_mensuales_usuarios(user_id);

-- Contadores
CREATE INDEX IF NOT EXISTS idx_contadores_impresora_fecha 
    ON contadores_impresora(printer_id, fecha_lectura DESC);

CREATE INDEX IF NOT EXISTS idx_contadores_usuario_fecha 
    ON contadores_usuario(printer_id, user_id, fecha_lectura DESC);
