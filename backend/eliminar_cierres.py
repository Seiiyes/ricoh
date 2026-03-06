#!/usr/bin/env python3
"""
Script para eliminar todos los cierres y poder recrearlos con la lógica corregida
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario


def eliminar_cierres(confirmar=True):
    """Eliminar todos los cierres"""
    db = next(get_db())
    
    try:
        # Contar cierres antes
        total_cierres = db.query(CierreMensual).count()
        total_usuarios = db.query(CierreMensualUsuario).count()
        
        print("=" * 80)
        print("🗑️  ELIMINAR CIERRES")
        print("=" * 80)
        print()
        print(f"Cierres a eliminar: {total_cierres}")
        print(f"Usuarios en cierres: {total_usuarios}")
        print()
        
        if total_cierres == 0:
            print("✅ No hay cierres para eliminar")
            return
        
        # Confirmar
        if confirmar:
            respuesta = input("¿Estás seguro de eliminar todos los cierres? (si/no): ")
            if respuesta.lower() not in ['si', 's', 'yes', 'y']:
                print("❌ Operación cancelada")
                return
        
        # Eliminar usuarios de cierres primero (por foreign key)
        db.query(CierreMensualUsuario).delete()
        print(f"✅ Eliminados {total_usuarios} usuarios de cierres")
        
        # Eliminar cierres
        db.query(CierreMensual).delete()
        print(f"✅ Eliminados {total_cierres} cierres")
        
        db.commit()
        
        print()
        print("=" * 80)
        print("✅ CIERRES ELIMINADOS EXITOSAMENTE")
        print("=" * 80)
        print()
        print("Ahora puedes recrear los cierres con la lógica corregida usando:")
        print("  python test_sistema_unificado.py")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Si se pasa --force, no pedir confirmación
    confirmar = '--force' not in sys.argv
    eliminar_cierres(confirmar)
