"""Script simple para verificar migraciones sin dependencias del backend"""
import os

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ ERROR: psycopg2 no está instalado")
    print("Instala con: pip install psycopg2-binary")
    exit(1)

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'ricoh_fleet',
    'user': 'ricoh_admin',
    'password': 'ricoh_secure_2024',
    'host': 'localhost',
    'port': '5432'
}

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
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    encontrados = 0
    faltantes = 0
    
    for idx in indices_esperados:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE indexname = %s AND schemaname = 'public'
            )
        """, (idx,))
        existe = cur.fetchone()[0]
        
        if existe:
            print(f'✅ {idx}')
            encontrados += 1
        else:
            print(f'❌ {idx} - NO ENCONTRADO')
            faltantes += 1
    
    cur.close()
    conn.close()
    
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
        'get_evolucion_consumo',
        'get_comparativa_periodos'
    ]
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    encontradas = 0
    faltantes = 0
    
    for func in funciones_esperadas:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_proc 
                WHERE proname = %s
            )
        """, (func,))
        existe = cur.fetchone()[0]
        
        if existe:
            print(f'✅ {func}()')
            encontradas += 1
        else:
            print(f'❌ {func}() - NO ENCONTRADA')
            faltantes += 1
    
    cur.close()
    conn.close()
    
    print(f'\nResumen: {encontradas}/{len(funciones_esperadas)} funciones encontradas')
    return faltantes == 0

def verificar_tabla_auditoria():
    """Verificar tabla de auditoría de la migración 014"""
    print('\n' + '=' * 60)
    print('VERIFICANDO TABLA DE AUDITORÍA (Migración 014)')
    print('=' * 60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Verificar tabla
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'auditoria_sistema'
        )
    """)
    tabla_existe = cur.fetchone()[0]
    
    if tabla_existe:
        print('✅ Tabla auditoria_sistema')
        
        # Verificar triggers
        triggers_esperados = ['auditar_aprovisionamiento', 'auditar_cierre']
        triggers_ok = True
        
        for trigger in triggers_esperados:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.triggers 
                    WHERE trigger_schema = 'public'
                    AND trigger_name = %s
                )
            """, (trigger,))
            existe = cur.fetchone()[0]
            
            if existe:
                print(f'✅ Trigger {trigger}')
            else:
                print(f'❌ Trigger {trigger} - NO ENCONTRADO')
                triggers_ok = False
        
        cur.close()
        conn.close()
        return triggers_ok
    else:
        print('❌ Tabla auditoria_sistema - NO ENCONTRADA')
        cur.close()
        conn.close()
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
            print('\nEl Sprint 5 está completamente implementado en la base de datos.')
        else:
            print('❌ FALTAN MIGRACIONES POR APLICAR')
            print('\nPara aplicar las migraciones faltantes:')
            print('1. Ejecuta: python apply_sprint5_migrations.py')
            print('2. O aplica manualmente los archivos SQL en backend/db/migrations/')
            
    except psycopg2.OperationalError as e:
        print(f'\n❌ ERROR DE CONEXIÓN: {e}')
        print('\nVerifica que:')
        print('1. PostgreSQL esté corriendo')
        print('2. Las credenciales sean correctas')
        print('3. La base de datos "ricoh_fleet" exista')
    except Exception as e:
        print(f'\n❌ ERROR: {e}')

if __name__ == '__main__':
    main()
