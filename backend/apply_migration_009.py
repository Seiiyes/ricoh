#!/usr/bin/env python3
"""
Script para aplicar migración 009: Permitir Solapamientos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from sqlalchemy import text


def apply_migration_009():
    """Aplica la migración 009"""
    
    print("=" * 80)
    print("🔧 APLICANDO MIGRACIÓN 009")
    print("=" * 80)
    print()
    print("Descripción: Permitir Solapamientos de Cierres")
    print()
    print("Cambios:")
    print("1. Eliminar trigger de no solapamiento")
    print("2. Eliminar función de validación")
    print("3. Agregar constraint de unicidad por tipo+período")
    print()
    print("Esto permite:")
    print("  ✅ Cierre mensual de marzo + Cierre diario del 3 de marzo")
    print("  ✅ Cierre semanal + Cierres diarios de esa semana")
    print("  ❌ Cierre mensual de marzo + Cierre mensual de marzo (duplicado)")
    print()
    
    db = next(get_db())
    
    try:
        # Leer archivo de migración
        migration_file = os.path.join(
            os.path.dirname(__file__),
            'migrations',
            '009_permitir_solapamientos.sql'
        )
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Ejecutar migración
        db.execute(text(migration_sql))
        db.commit()
        
        print()
        print("=" * 80)
        print("✅ MIGRACIÓN 009 APLICADA EXITOSAMENTE")
        print("=" * 80)
        print()
        print("Ahora puedes crear múltiples cierres del mismo período:")
        print("  - Cierre mensual de marzo")
        print("  - Cierre diario del 1 de marzo")
        print("  - Cierre diario del 2 de marzo")
        print("  - Cierre semanal de la primera semana")
        print()
        print("Todos pueden coexistir y compararlos después.")
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
    success = apply_migration_009()
    sys.exit(0 if success else 1)
