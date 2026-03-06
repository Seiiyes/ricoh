-- Migration 006: Add detailed counter fields for printer 252 format
-- Adds columns for "Hojas a 2 caras" and "Páginas combinadas" metrics

-- Add Copiadora detailed fields
ALTER TABLE contadores_usuario 
ADD COLUMN IF NOT EXISTS copiadora_hojas_2_caras INTEGER DEFAULT 0 NOT NULL;

ALTER TABLE contadores_usuario 
ADD COLUMN IF NOT EXISTS copiadora_paginas_combinadas INTEGER DEFAULT 0 NOT NULL;

-- Add Impresora detailed fields
ALTER TABLE contadores_usuario 
ADD COLUMN IF NOT EXISTS impresora_hojas_2_caras INTEGER DEFAULT 0 NOT NULL;

ALTER TABLE contadores_usuario 
ADD COLUMN IF NOT EXISTS impresora_paginas_combinadas INTEGER DEFAULT 0 NOT NULL;
