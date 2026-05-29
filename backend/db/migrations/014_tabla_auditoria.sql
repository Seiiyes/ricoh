CREATE TABLE auditoria_sistema (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tipo VARCHAR(50) NOT NULL,
    descripcion TEXT NOT NULL,
    usuario VARCHAR(100),
    printer_id INTEGER REFERENCES printers(id) ON DELETE SET NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    metadata JSONB,
    
    CONSTRAINT auditoria_sistema_status_check CHECK (status IN ('success', 'error', 'warning'))
);

CREATE INDEX idx_auditoria_fecha ON auditoria_sistema(fecha DESC);
CREATE INDEX idx_auditoria_tipo ON auditoria_sistema(tipo);
CREATE INDEX idx_auditoria_status ON auditoria_sistema(status);

-- Trigger para auditar aprovisionamiento
CREATE OR REPLACE FUNCTION trigger_auditar_aprovisionamiento()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_sistema (tipo, descripcion, usuario, printer_id, user_id, status)
    VALUES (
        'Aprovisionamiento',
        'Usuario asignado a impresora',
        CURRENT_USER,
        NEW.printer_id,
        NEW.user_id,
        'success'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auditar_aprovisionamiento
AFTER INSERT ON user_printer_assignments
FOR EACH ROW
EXECUTE FUNCTION trigger_auditar_aprovisionamiento();

-- Trigger para auditar cierres
CREATE OR REPLACE FUNCTION trigger_auditar_cierre()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria_sistema (tipo, descripcion, usuario, printer_id, status)
    VALUES (
        'Cierre Mensual',
        'Cierre ejecutado para ' || TO_CHAR(NEW.fecha_inicio, 'DD/MM/YYYY') || ' - ' || TO_CHAR(NEW.fecha_fin, 'DD/MM/YYYY'),
        NEW.cerrado_por,
        NEW.printer_id,
        'success'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER auditar_cierre
AFTER INSERT ON cierres_mensuales
FOR EACH ROW
EXECUTE FUNCTION trigger_auditar_cierre();
