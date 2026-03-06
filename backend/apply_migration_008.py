#!/usr/bin/env python3
"""
Script para aplicar migración 008: Generalizar Sistema de Cierres
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from sqlalchemy import text


def apply_migration_008():
    """Aplica la migración 008"""
    
    print("=" * 80)
    print("🔧 APLICANDO MIGRACIÓN 008")
    print("=" * 80)
    print()
    print("Descripción: Generalizar Sistema de Cierres")
    print()
    print("Cambios:")
    print("1. Agregar campos: tipo_periodo, fecha_inicio, fecha_fin")
    print("2. Migrar datos existentes")
    print("3. Agregar validaciones y constraints")
    print("4. Crear índices optimizados")
    print("5. Agregar trigger de no solapamiento")
    print("6. Crear vista de resumen")
    print("7. Crear función auxiliar")
    print()
    
    respuesta = input("¿Desea continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Migración cancelada")
        return False
    
    print()
    print("⏳ Aplicando migración...")
    print()
    
    db = next(get_db())
    
    try:
        # Leer archivo de migración
        migration_file = os.path.join(
            os.path.dirname(__file__),
            'migrations',
            '008_generalizar_cierres.sql'
        )
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Ejecutar migración
        db.execute(text(migration_sql))
        db.commit()
        
        print()
        print("=" * 80)
        print("✅ MIGRACIÓN 008 APLICADA EXITOSAMENTE")
        print("=" * 80)
        print()
        
        # Verificar cambios
        print("📊 VERIFICACIÓN:")
        print("-" * 80)
        
        # Contar cierres por tipo
        result = db.execute(text("""
            SELECT 
                tipo_periodo,
                COUNT(*) as total,
                MIN(fecha_inicio) as primera_fecha,
                MAX(fecha_fin) as ultima_fecha
            FROM cierres_mensuales
            GROUP BY tipo_periodo
            ORDER BY tipo_periodo
        """))
        
        print("Cierres por tipo:")
        for row in result:
            print(f"  {row.tipo_periodo:15s}: {row.total:3d} cierres "
                  f"(desde {row.primera_fecha} hasta {row.ultima_fecha})")
        
        print()
        
        # Verificar vista
        result = db.execute(text("""
            SELECT COUNT(*) as total
            FROM v_cierres_resumen
        """))
        
        total_vista = result.scalar()
        print(f"Vista v_cierres_resumen: {total_vista} registros")
        
        print()
        
        # Verificar función
        result = db.execute(text("""
            SELECT proname, pronargs
            FROM pg_proc
            WHERE proname = 'get_ultimo_cierre'
        """))
        
        if result.rowcount > 0:
            print("Función get_ultimo_cierre: ✅ Creada")
        
        print()
        
        # Verificar trigger
        result = db.execute(text("""
            SELECT tgname
            FROM pg_trigger
            WHERE tgname = 'trigger_check_no_solapamiento_cierres'
        """))
        
        if result.rowcount > 0:
            print("Trigger check_no_solapamiento_cierres: ✅ Creado")
        
        print()
        print("=" * 80)
        print("✅ Sistema de cierres generalizado correctamente")
        print("=" * 80)
        print()
        print("Ahora puedes crear cierres de cualquier tipo:")
        print("  - Diarios: Para monitoreo día a día")
        print("  - Semanales: Para reportes semanales")
        print("  - Mensuales: Para auditoría oficial")
        print("  - Personalizados: Para cualquier período")
        print()
        
        return True
        
    except Exception as e:
        db.rollback()
        print()
        print("=" * 80)
        print("❌ ERROR AL APLICAR MIGRACIÓN")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = apply_migration_008()
    sys.exit(0 if success else 1)
