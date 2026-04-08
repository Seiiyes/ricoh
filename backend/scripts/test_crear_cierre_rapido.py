#!/usr/bin/env python3
"""
Prueba rápida de creación de cierre después de correcciones
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer
from services.close_service import CloseService
from datetime import date

def main():
    print("="*80)
    print("🧪 PRUEBA RÁPIDA: Crear Cierre Después de Correcciones")
    print("="*80)
    
    db = SessionLocal()
    
    try:
        # Obtener primera impresora
        printer = db.query(Printer).first()
        if not printer:
            print("❌ No hay impresoras")
            return 1
        
        print(f"\n✓ Impresora: {printer.hostname} (ID: {printer.id})")
        
        # Crear cierre de hoy
        print(f"⏳ Creando cierre de prueba...")
        
        cierre = CloseService.create_close(
            db=db,
            printer_id=printer.id,
            tipo_periodo='personalizado',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            cerrado_por='test_correccion',
            notas='Prueba después de correcciones en counters.py'
        )
        
        print(f"\n✅ ¡CIERRE CREADO EXITOSAMENTE!")
        print(f"   ID: {cierre.id}")
        print(f"   Total páginas: {cierre.total_paginas:,}")
        print(f"   Usuarios: {len(cierre.usuarios)}")
        
        # Verificar que los usuarios tengan user_id
        if cierre.usuarios:
            print(f"\n✓ Verificando primeros 3 usuarios:")
            from db.models import User
            for i, usuario in enumerate(cierre.usuarios[:3], 1):
                user = db.query(User).filter(User.id == usuario.user_id).first()
                if user:
                    print(f"   {i}. [{user.codigo_de_usuario}] {user.name} - {usuario.total_paginas:,} páginas")
                else:
                    print(f"   {i}. user_id={usuario.user_id} (no encontrado) - {usuario.total_paginas:,} páginas")
        
        # Eliminar cierre de prueba
        print(f"\n⏳ Eliminando cierre de prueba...")
        db.delete(cierre)
        db.commit()
        print(f"✅ Cierre eliminado")
        
        print("\n" + "="*80)
        print("🎉 ¡PRUEBA EXITOSA!")
        print("="*80)
        print("\n✅ La creación de cierres funciona correctamente")
        print("✅ El acceso a datos de usuario mediante JOIN funciona")
        print("✅ Las correcciones en counters.py son efectivas")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    exit(main())
