-- Script SQL para verificar migraciones del Sprint 5

\echo '========================================='
\echo 'VERIFICANDO ÍNDICES (Migración 012)'
\echo '========================================='

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_printers_status') 
        THEN '✅ idx_printers_status'
        ELSE '❌ idx_printers_status - NO ENCONTRADO'
    END as status
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_printers_empresa_status') 
        THEN '✅ idx_printers_empresa_status'
        ELSE '❌ idx_printers_empresa_status - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_assignments_active') 
        THEN '✅ idx_user_assignments_active'
        ELSE '❌ idx_user_assignments_active - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_cierres_periodo') 
        THEN '✅ idx_cierres_periodo'
        ELSE '❌ idx_cierres_periodo - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_cierres_printer_periodo') 
        THEN '✅ idx_cierres_printer_periodo'
        ELSE '❌ idx_cierres_printer_periodo - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_cierres_fecha_rango') 
        THEN '✅ idx_cierres_fecha_rango'
        ELSE '❌ idx_cierres_fecha_rango - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_cierres_usuarios_cierre') 
        THEN '✅ idx_cierres_usuarios_cierre'
        ELSE '❌ idx_cierres_usuarios_cierre - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_cierres_usuarios_user') 
        THEN '✅ idx_cierres_usuarios_user'
        ELSE '❌ idx_cierres_usuarios_user - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_contadores_impresora_fecha') 
        THEN '✅ idx_contadores_impresora_fecha'
        ELSE '❌ idx_contadores_impresora_fecha - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_contadores_usuario_fecha') 
        THEN '✅ idx_contadores_usuario_fecha'
        ELSE '❌ idx_contadores_usuario_fecha - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_auditoria_fecha') 
        THEN '✅ idx_auditoria_fecha'
        ELSE '❌ idx_auditoria_fecha - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_auditoria_tipo') 
        THEN '✅ idx_auditoria_tipo'
        ELSE '❌ idx_auditoria_tipo - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_auditoria_status') 
        THEN '✅ idx_auditoria_status'
        ELSE '❌ idx_auditoria_status - NO ENCONTRADO'
    END;

\echo ''
\echo '========================================='
\echo 'VERIFICANDO FUNCIONES (Migración 013)'
\echo '========================================='

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_dashboard_kpis') 
        THEN '✅ get_dashboard_kpis()'
        ELSE '❌ get_dashboard_kpis() - NO ENCONTRADA'
    END as status
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_top_impresoras') 
        THEN '✅ get_top_impresoras()'
        ELSE '❌ get_top_impresoras() - NO ENCONTRADA'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_evolucion_consumo') 
        THEN '✅ get_evolucion_consumo()'
        ELSE '❌ get_evolucion_consumo() - NO ENCONTRADA'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_comparativa_periodos') 
        THEN '✅ get_comparativa_periodos()'
        ELSE '❌ get_comparativa_periodos() - NO ENCONTRADA'
    END;

\echo ''
\echo '========================================='
\echo 'VERIFICANDO TABLA AUDITORÍA (Migración 014)'
\echo '========================================='

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'auditoria_sistema') 
        THEN '✅ Tabla auditoria_sistema'
        ELSE '❌ Tabla auditoria_sistema - NO ENCONTRADA'
    END as status
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'auditar_aprovisionamiento') 
        THEN '✅ Trigger auditar_aprovisionamiento'
        ELSE '❌ Trigger auditar_aprovisionamiento - NO ENCONTRADO'
    END
UNION ALL
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.triggers WHERE trigger_name = 'auditar_cierre') 
        THEN '✅ Trigger auditar_cierre'
        ELSE '❌ Trigger auditar_cierre - NO ENCONTRADO'
    END;

\echo ''
\echo '========================================='
\echo 'RESUMEN'
\echo '========================================='
