"""Script para verificar si las migraciones del Sprint 5 fueron ejecutadas"""
import sys
from db.database import engine
from sqlalchemy import text

def verificar_indices():
    """Verificar índices de la migración 012"""
    print('=' * 60)
    print('VERIFICANDO ÍNDICES (Migración 012)')
    print('=' * 60)
    
    indices_esperados = [
        'idx_printers_status',
        'idx_printers_empresa_status',
        'idx_user_assignments_active',
        'idx_cierres_periodo',
        'idx_cierres_printer_periodo',
        'idx_cierres_fecha_rango',
        'idx_cierres_usuarios_cierre',
        'idx_cierres_usuarios_user',
        'idx_contadores_impresora_fecha',
        'idx_contadores_usuario_fecha',
        'idx_auditoria_fecha',
        'idx_auditoria_tipo',
        'idx_auditoria_status'
    ]
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE indexname LIKE 'idx_%' 
            AND schemaname = 'public'
            ORDER BY indexname
        """))
        indices_encontrados = [row[0] for row in result]
    
    encontrados = 0
    faltantes = 0
    
    for idx in indices_esperados:
        if idx in indices_encontrados:
            print(f'✅ {idx}')
            encontrados += 1
        else:
            print(f'❌ {idx} - NO ENCONTRADO')
            faltantes += 1
    
    print(f'\nResumen: {encontrados}/{len(indices_esperados)} índices encontrados')
    return faltantes == 0

def verificar_funciones():
    """Verificar funciones almacenadas de la migración 013"""
    print('\n' + '=' * 60)
    print('VERIFICANDO FUNCIONES ALMACENADAS (Migración 013)')
    print('=' * 60)
    
    funciones_esperadas = [
        'get_dashboard_kpis',
        'get_top_impresoras',
        'get_top_consumo_usuarios',
        'get_evolucion_consumo',
        'get_comparativa_periodos'
    ]
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_type = 'FUNCTION' 
            AND routine_schema = 'public'
            AND routine_name LIKE 'get_%'
            ORDER BY routine_name
        """))
        funciones_encontradas = [row[0] for row in result]
    
    encontradas = 0
    faltantes = 0
    
    for func in funciones_esperadas:
        if func in funciones_encontradas:
            print(f'✅ {func}()')
            encontradas += 1
        else:
            print(f'❌ {func}() - NO ENCONTRADA')
            faltantes += 1
    
    print(f'\nResumen: {encontradas}/{len(funciones_esperadas)} funciones encontradas')
    return faltantes == 0

def verificar_tabla_auditoria():
    """Verificar tabla de auditoría de la migración 014"""
    print('\n' + '=' * 60)
    print('VERIFICANDO TABLA DE AUDITORÍA (Migración 014)')
    print('=' * 60)
    
    with engine.connect() as conn:
        # Verificar tabla
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'auditoria_sistema'
            )
        """))
        tabla_existe = result.scalar()
        
        if tabla_existe:
            print('✅ Tabla auditoria_sistema')
            
            # Verificar triggers
            result = conn.execute(text("""
                SELECT trigger_name 
                FROM information_schema.triggers 
                WHERE trigger_schema = 'public'
                AND trigger_name LIKE 'auditar_%'
                ORDER BY trigger_name
            """))
            triggers = [row[0] for row in result]
            
            triggers_esperados = ['auditar_aprovisionamiento', 'auditar_cierre']
            
            for trigger in triggers_esperados:
                if trigger in triggers:
                    print(f'✅ Trigger {trigger}')
                else:
                    print(f'❌ Trigger {trigger} - NO ENCONTRADO')
            
            return len(triggers) == len(triggers_esperados)
        else:
            print('❌ Tabla auditoria_sistema - NO ENCONTRADA')
            return False

def main():
    print('\n🔍 VERIFICACIÓN DE MIGRACIONES DEL SPRINT 5\n')
    
    try:
        indices_ok = verificar_indices()
        funciones_ok = verificar_funciones()
        auditoria_ok = verificar_tabla_auditoria()
        
        print('\n' + '=' * 60)
        print('RESUMEN FINAL')
        print('=' * 60)
        
        if indices_ok and funciones_ok and auditoria_ok:
            print('✅ TODAS LAS MIGRACIONES ESTÁN APLICADAS')
            return 0
        else:
            print('❌ FALTAN MIGRACIONES POR APLICAR')
            print('\nPara aplicar las migraciones, ejecuta:')
            print('  python backend/apply_migrations.py')
            return 1
            
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
