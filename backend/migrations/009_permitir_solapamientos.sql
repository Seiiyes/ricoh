-- ============================================================================
-- MIGRACIÓN 009: Permitir Solapamientos de Cierres
-- ============================================================================
-- Descripción: Elimina el trigger que previene solapamientos para permitir
--              múltiples cierres del mismo período (ej: mensual + diarios)
--
-- Cambios:
-- 1. Eliminar trigger de no solapamiento
-- 2. Eliminar función de validación
-- 3. Agregar constraint de unicidad por tipo+período
-- ============================================================================

BEGIN;

-- Eliminar trigger
DROP TRIGGER IF EXISTS trigger_check_no_solapamiento_cierres ON cierres_mensuales;

-- Eliminar función
DROP FUNCTION IF EXISTS check_no_solapamiento_cierres();

-- Agregar constraint de unicidad: mismo tipo + mismo período = duplicado
-- Esto permite: mensual de marzo + diario del 3 de marzo (OK)
-- Pero previene: mensual de marzo + mensual de marzo (ERROR)
ALTER TABLE cierres_mensuales
DROP CONSTRAINT IF EXISTS unique_tipo_periodo;

ALTER TABLE cierres_mensuales
ADD CONSTRAINT unique_tipo_periodo 
UNIQUE (printer_id, tipo_periodo, fecha_inicio, fecha_fin);

COMMENT ON CONSTRAINT unique_tipo_periodo ON cierres_mensuales IS
'Previene duplicados del mismo tipo y período, pero permite solapamientos de diferentes tipos';

-- Eliminar índice de solapamiento (ya no es necesario)
DROP INDEX IF EXISTS idx_cierres_solapamiento;

COMMIT;

-- Verificación
DO $$
BEGIN
    RAISE NOTICE '✅ Migración 009 completada';
    RAISE NOTICE '   - Trigger eliminado: trigger_check_no_solapamiento_cierres';
    RAISE NOTICE '   - Función eliminada: check_no_solapamiento_cierres()';
    RAISE NOTICE '   - Constraint agregado: unique_tipo_periodo';
    RAISE NOTICE '   - Ahora se permiten solapamientos de diferentes tipos';
END $$;
