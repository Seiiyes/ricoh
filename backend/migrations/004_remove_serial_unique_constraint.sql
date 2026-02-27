-- Migration 004: Remove unique constraint from serial_number
-- Allows multiple printers with NULL serial_number

-- Drop the unique constraint on serial_number
ALTER TABLE printers DROP CONSTRAINT IF EXISTS printers_serial_number_key;

-- Add index for performance (non-unique)
CREATE INDEX IF NOT EXISTS idx_printers_serial_number ON printers(serial_number);
