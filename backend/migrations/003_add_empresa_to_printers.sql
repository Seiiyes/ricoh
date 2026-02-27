-- Migration 003: Add empresa field to printers table
-- Date: 2026-02-27
-- Description: Adds empresa (company) field to printers for organization

-- Add empresa column to printers table
ALTER TABLE printers 
ADD COLUMN IF NOT EXISTS empresa VARCHAR(255);

-- Add index for faster filtering by empresa
CREATE INDEX IF NOT EXISTS idx_printers_empresa ON printers(empresa);

-- Update existing printers with default value (optional)
-- UPDATE printers SET empresa = 'Sin asignar' WHERE empresa IS NULL;

COMMENT ON COLUMN printers.empresa IS 'Empresa a la que pertenece la impresora';
