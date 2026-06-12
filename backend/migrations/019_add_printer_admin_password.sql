-- Migration: 019_add_printer_admin_password
-- Description: Agrega el campo admin_password a la tabla printers

ALTER TABLE printers ADD COLUMN IF NOT EXISTS admin_password VARCHAR(255) NULL;
