#!/usr/bin/env python3
"""
Script para recrear cierres con la lógica corregida
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from services.close_service import CloseService


def recrear_cierres():
    """Recrear cierres de prueba"""
    db = next(get_db())
    
    try:
        print("=" * 80)
        print("🔄 RECREAR CIERRES CON LÓGICA CORREGIDA")
        print("=" * 80)
        print()
        
        # Crear cierre diario del 2 de marzo para impresora 4
        print("Creando cierre diario 2 de marzo 2026 para impresora 4...")
        cierre1 = CloseService.create_close(
            db=db,
            printer_id=4,
            fecha_inicio=date(2026, 3, 2),
            fecha_fin=date(2026, 3, 2),
            tipo_periodo='diario',
            cerrado_por='admin',
            notas='Cierre diario recreado con lógica corregida'
        )
        print(f"✅ Cierre creado: ID {cierre1.id}")
        print(f"   Total páginas: {cierre1.total_paginas:,}")
        print(f"   Diferencia: {cierre1.diferencia_total:,}")
        print(f"   Usuarios: {len(cierre1.usuarios)}")
        
        # Verificar que los usuarios tengan consumo > 0
        usuarios_con_consumo = [u for u in cierre1.usuarios if u.consumo_total > 0]
        print(f"   Usuarios con consumo > 0: {len(usuarios_con_consumo)}")
        
        if len(usuarios_con_consumo) > 0:
            print(f"   Top 5 usuarios:")
            for u in sorted(cierre1.usuarios, key=lambda x: x.consumo_total, reverse=True)[:5]:
                print(f"     - {u.nombre_usuario}: {u.consumo_total:,} páginas")
        
        print()
        
        # Crear cierre diario del 3 de marzo para impresora 4
        print("Creando cierre diario 3 de marzo 2026 para impresora 4...")
        cierre2 = CloseService.create_close(
            db=db,
            printer_id=4,
            fecha_inicio=date(2026, 3, 3),
            fecha_fin=date(2026, 3, 3),
            tipo_periodo='diario',
            cerrado_por='admin',
            notas='Cierre diario recreado con lógica corregida'
        )
        print(f"✅ Cierre creado: ID {cierre2.id}")
        print(f"   Total páginas: {cierre2.total_paginas:,}")
        print(f"   Diferencia: {cierre2.diferencia_total:,}")
        print(f"   Usuarios: {len(cierre2.usuarios)}")
        
        usuarios_con_consumo = [u for u in cierre2.usuarios if u.consumo_total > 0]
        print(f"   Usuarios con consumo > 0: {len(usuarios_con_consumo)}")
        
        if len(usuarios_con_consumo) > 0:
            print(f"   Top 5 usuarios:")
            for u in sorted(cierre2.usuarios, key=lambda x: x.consumo_total, reverse=True)[:5]:
                print(f"     - {u.nombre_usuario}: {u.consumo_total:,} páginas")
        
        print()
        print("=" * 80)
        print("✅ CIERRES RECREADOS EXITOSAMENTE")
        print("=" * 80)
        print()
        print("Ahora puedes verificar en el frontend que se muestren correctamente")
        print("URL: http://localhost:5173")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    recrear_cierres()
