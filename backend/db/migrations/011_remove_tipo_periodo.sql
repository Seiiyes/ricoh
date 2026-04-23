-- ============================================================================
-- MIGRACIÓN 011: Eliminar campo tipo_periodo
-- ============================================================================
-- Fecha: 21 de abril de 2026
-- Descripción: Elimina el campo tipo_periodo de la tabla cierres_mensuales
--              ya que un cierre es simplemente un snapshot de contadores
--              y el usuario decide cómo interpretarlo.
-- 
-- IMPORTANTE: Backup creado antes de esta migración:
--             backups/backup_pre_tipo_periodo_removal_20260421_081556.sql
-- ============================================================================

BEGIN;

-- 1. Eliminar columna tipo_periodo
ALTER TABLE cierres_mensuales DROP COLUMN IF EXISTS tipo_periodo;

-- 2. Actualizar comentario de la tabla
COMMENT ON TABLE cierres_mensuales IS 
'Cierres de contadores - Snapshots inmutables para auditoría y comparación.
Un cierre es simplemente un snapshot de contadores en un momento dado.
El usuario decide cómo interpretarlo (diario, semanal, mensual, etc.)';

-- 3. Verificar que la columna fue eliminada
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'cierres_mensuales' 
        AND column_name = 'tipo_periodo'
    ) THEN
        RAISE EXCEPTION 'Error: La columna tipo_periodo no fue eliminada correctamente';
    END IF;
    
    RAISE NOTICE 'Migración 011 completada exitosamente';
END $$;

COMMIT;
