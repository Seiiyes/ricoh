-- Migración 020: Tabla de programación de cierres masivos
CREATE TABLE IF NOT EXISTS scheduled_closures (
    id SERIAL PRIMARY KEY,
    frequency VARCHAR(50) NOT NULL,
    scheduled_time VARCHAR(5) NOT NULL,
    specific_date DATE,
    day_of_week INTEGER,
    day_of_month INTEGER,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    notas TEXT,
    created_by VARCHAR(100) NOT NULL,
    last_run TIMESTAMP WITH TIME ZONE,
    next_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_scheduled_closures_active ON scheduled_closures(is_active);
CREATE INDEX IF NOT EXISTS idx_scheduled_closures_next_run ON scheduled_closures(next_run);
