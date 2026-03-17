-- Agregar campos de capacidades a la tabla printers
ALTER TABLE printers ADD COLUMN IF NOT EXISTS soporta_color BOOLEAN DEFAULT FALSE;
ALTER TABLE printers ADD COLUMN IF NOT EXISTS soporta_fax BOOLEAN DEFAULT FALSE;
ALTER TABLE printers ADD COLUMN IF NOT EXISTS soporta_escaner BOOLEAN DEFAULT FALSE;
ALTER TABLE printers ADD COLUMN IF NOT EXISTS formato_contadores VARCHAR(50) DEFAULT 'estandar';

-- Comentarios
COMMENT ON COLUMN printers.soporta_color IS 'Indica si la impresora soporta impresión a color';
COMMENT ON COLUMN printers.soporta_fax IS 'Indica si la impresora tiene funcionalidad de fax';
COMMENT ON COLUMN printers.soporta_escaner IS 'Indica si la impresora tiene funcionalidad de escáner';
COMMENT ON COLUMN printers.formato_contadores IS 'Formato de contadores: estandar (18 cols), simplificado (13 cols), ecologico';
