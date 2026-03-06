-- Migration 005: Add Counter Tables
-- Fecha: 2026-03-02
-- Descripción: Agrega tablas para almacenar contadores de impresoras y usuarios

-- 1. Agregar campos de configuración de contadores a la tabla printers
ALTER TABLE printers 
ADD COLUMN IF NOT EXISTS tiene_contador_usuario BOOLEAN DEFAULT TRUE NOT NULL;

ALTER TABLE printers 
ADD COLUMN IF NOT EXISTS usar_contador_ecologico BOOLEAN DEFAULT FALSE NOT NULL;

-- Configurar impresora ID 6 (B/N sin contador por usuario)
UPDATE printers 
SET tiene_contador_usuario = FALSE, 
    usar_contador_ecologico = TRUE 
WHERE id = 6;

-- 2. Crear tabla contadores_impresora
CREATE TABLE IF NOT EXISTS contadores_impresora (
    id SERIAL PRIMARY KEY,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    
    -- Contador total
    total INTEGER DEFAULT 0 NOT NULL,
    
    -- Copiadora
    copiadora_bn INTEGER DEFAULT 0 NOT NULL,
    copiadora_color INTEGER DEFAULT 0 NOT NULL,
    copiadora_color_personalizado INTEGER DEFAULT 0 NOT NULL,
    copiadora_dos_colores INTEGER DEFAULT 0 NOT NULL,
    
    -- Impresora
    impresora_bn INTEGER DEFAULT 0 NOT NULL,
    impresora_color INTEGER DEFAULT 0 NOT NULL,
    impresora_color_personalizado INTEGER DEFAULT 0 NOT NULL,
    impresora_dos_colores INTEGER DEFAULT 0 NOT NULL,
    
    -- Fax
    fax_bn INTEGER DEFAULT 0 NOT NULL,
    
    -- Enviar/TX Total
    enviar_total_bn INTEGER DEFAULT 0 NOT NULL,
    enviar_total_color INTEGER DEFAULT 0 NOT NULL,
    
    -- Transmisión por fax
    transmision_fax_total INTEGER DEFAULT 0 NOT NULL,
    
    -- Envío por escáner
    envio_escaner_bn INTEGER DEFAULT 0 NOT NULL,
    envio_escaner_color INTEGER DEFAULT 0 NOT NULL,
    
    -- Otras funciones
    otras_a3_dlt INTEGER DEFAULT 0 NOT NULL,
    otras_duplex INTEGER DEFAULT 0 NOT NULL,
    
    -- Metadata
    fecha_lectura TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para contadores_impresora
CREATE INDEX IF NOT EXISTS idx_contadores_impresora_printer_id ON contadores_impresora(printer_id);
CREATE INDEX IF NOT EXISTS idx_contadores_impresora_fecha_lectura ON contadores_impresora(fecha_lectura);

-- 3. Crear tabla contadores_usuario
CREATE TABLE IF NOT EXISTS contadores_usuario (
    id SERIAL PRIMARY KEY,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    
    -- Usuario
    codigo_usuario VARCHAR(8) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    
    -- Total impresiones
    total_paginas INTEGER DEFAULT 0 NOT NULL,
    total_bn INTEGER DEFAULT 0 NOT NULL,
    total_color INTEGER DEFAULT 0 NOT NULL,
    
    -- Copiadora (getUserCounter)
    copiadora_bn INTEGER DEFAULT 0 NOT NULL,
    copiadora_mono_color INTEGER DEFAULT 0 NOT NULL,
    copiadora_dos_colores INTEGER DEFAULT 0 NOT NULL,
    copiadora_todo_color INTEGER DEFAULT 0 NOT NULL,
    
    -- Impresora (getUserCounter)
    impresora_bn INTEGER DEFAULT 0 NOT NULL,
    impresora_mono_color INTEGER DEFAULT 0 NOT NULL,
    impresora_dos_colores INTEGER DEFAULT 0 NOT NULL,
    impresora_color INTEGER DEFAULT 0 NOT NULL,
    
    -- Escáner (getUserCounter)
    escaner_bn INTEGER DEFAULT 0 NOT NULL,
    escaner_todo_color INTEGER DEFAULT 0 NOT NULL,
    
    -- Fax (getUserCounter)
    fax_bn INTEGER DEFAULT 0 NOT NULL,
    fax_paginas_transmitidas INTEGER DEFAULT 0 NOT NULL,
    
    -- Revelado (getUserCounter)
    revelado_negro INTEGER DEFAULT 0 NOT NULL,
    revelado_color_ymc INTEGER DEFAULT 0 NOT NULL,
    
    -- Métricas ecológicas (getEcoCounter)
    eco_uso_2_caras VARCHAR(50),
    eco_uso_combinar VARCHAR(50),
    eco_reduccion_papel VARCHAR(50),
    
    -- Tipo de contador usado
    tipo_contador VARCHAR(20) DEFAULT 'usuario' NOT NULL,
    
    -- Metadata
    fecha_lectura TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para contadores_usuario
CREATE INDEX IF NOT EXISTS idx_contadores_usuario_printer_id ON contadores_usuario(printer_id);
CREATE INDEX IF NOT EXISTS idx_contadores_usuario_codigo ON contadores_usuario(codigo_usuario);
CREATE INDEX IF NOT EXISTS idx_contadores_usuario_fecha_lectura ON contadores_usuario(fecha_lectura);

-- 4. Crear tabla cierres_mensuales
CREATE TABLE IF NOT EXISTS cierres_mensuales (
    id SERIAL PRIMARY KEY,
    printer_id INTEGER NOT NULL REFERENCES printers(id) ON DELETE CASCADE,
    
    -- Período
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    
    -- Contadores totales al cierre
    total_paginas INTEGER DEFAULT 0 NOT NULL,
    total_copiadora INTEGER DEFAULT 0 NOT NULL,
    total_impresora INTEGER DEFAULT 0 NOT NULL,
    total_escaner INTEGER DEFAULT 0 NOT NULL,
    total_fax INTEGER DEFAULT 0 NOT NULL,
    
    -- Diferencia con mes anterior
    diferencia_total INTEGER DEFAULT 0 NOT NULL,
    diferencia_copiadora INTEGER DEFAULT 0 NOT NULL,
    diferencia_impresora INTEGER DEFAULT 0 NOT NULL,
    diferencia_escaner INTEGER DEFAULT 0 NOT NULL,
    diferencia_fax INTEGER DEFAULT 0 NOT NULL,
    
    -- Metadata
    fecha_cierre TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cerrado_por VARCHAR(100),
    notas TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: un solo cierre por impresora por mes
    UNIQUE(printer_id, anio, mes)
);

-- Índices para cierres_mensuales
CREATE INDEX IF NOT EXISTS idx_cierres_mensuales_printer_id ON cierres_mensuales(printer_id);
CREATE INDEX IF NOT EXISTS idx_cierres_mensuales_anio ON cierres_mensuales(anio);
CREATE INDEX IF NOT EXISTS idx_cierres_mensuales_mes ON cierres_mensuales(mes);

-- Comentarios para documentación
COMMENT ON TABLE contadores_impresora IS 'Almacena contadores totales de cada impresora (getUnificationCounter.cgi)';
COMMENT ON TABLE contadores_usuario IS 'Almacena contadores individuales por usuario (getUserCounter.cgi o getEcoCounter.cgi)';
COMMENT ON TABLE cierres_mensuales IS 'Almacena snapshots mensuales de contadores para comparación';

COMMENT ON COLUMN printers.tiene_contador_usuario IS 'Indica si la impresora tiene getUserCounter.cgi disponible';
COMMENT ON COLUMN printers.usar_contador_ecologico IS 'Indica si se debe usar getEcoCounter.cgi para obtener contadores por usuario';
COMMENT ON COLUMN contadores_usuario.tipo_contador IS 'Tipo de contador: "usuario" (getUserCounter) o "ecologico" (getEcoCounter)';
