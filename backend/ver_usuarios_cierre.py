#!/usr/bin/env python3
"""
Script para ver los usuarios de un cierre específico
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario


def ver_usuarios_cierre(cierre_id: int):
    """Ver usuarios de un cierre"""
    db = next(get_db())
    
    try:
        # Obtener cierre
        cierre = db.query(CierreMensual).filter(CierreMensual.id == cierre_id).first()
        
        if not cierre:
            print(f"❌ Cierre {cierre_id} no encontrado")
            return
        
        print("=" * 80)
        print(f"📊 CIERRE ID: {cierre.id}")
        print("=" * 80)
        print()
        print(f"Impresora: {cierre.printer_id}")
        print(f"Tipo: {cierre.tipo_periodo}")
        print(f"Período: {cierre.fecha_inicio} a {cierre.fecha_fin}")
        print(f"Fecha de cierre: {cierre.fecha_cierre}")
        print(f"Cerrado por: {cierre.cerrado_por or 'N/A'}")
        print()
        print(f"Total páginas: {cierre.total_paginas:,}")
        print(f"Diferencia: {cierre.diferencia_total:,}")
        print()
        
        # Obtener usuarios
        usuarios = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre_id
        ).order_by(CierreMensualUsuario.consumo_total.desc()).all()
        
        print("=" * 80)
        print(f"👥 USUARIOS EN EL SNAPSHOT: {len(usuarios)}")
        print("=" * 80)
        print()
        
        if len(usuarios) == 0:
            print("⚠️  No hay usuarios en este cierre")
            print()
            print("Posibles causas:")
            print("  - El cierre se creó sin lecturas de usuarios")
            print("  - No había usuarios registrados en ese momento")
            print("  - Error al crear el snapshot")
            return
        
        # Mostrar top 20
        print("Top 20 usuarios por consumo:")
        print()
        print(f"{'#':<4} {'Usuario':<30} {'Código':<10} {'Consumo':<12} {'Total':<12}")
        print("-" * 80)
        
        for i, u in enumerate(usuarios[:20], 1):
            print(f"{i:<4} {u.nombre_usuario:<30} {u.codigo_usuario:<10} {u.consumo_total:>12,} {u.total_paginas:>12,}")
        
        print()
        print("=" * 80)
        print()
        
        # Estadísticas
        total_consumo = sum(u.consumo_total for u in usuarios)
        usuarios_activos = len([u for u in usuarios if u.consumo_total > 0])
        promedio = total_consumo / usuarios_activos if usuarios_activos > 0 else 0
        
        print("📊 Estadísticas:")
        print(f"  Total usuarios: {len(usuarios)}")
        print(f"  Usuarios activos (consumo > 0): {usuarios_activos}")
        print(f"  Suma de consumos: {total_consumo:,} páginas")
        print(f"  Promedio por usuario activo: {promedio:,.1f} páginas")
        print()
        
        # Comparar con total de impresora
        if cierre.diferencia_total > 0:
            diferencia_porcentual = abs(total_consumo - cierre.diferencia_total) / cierre.diferencia_total * 100
            print(f"  Total impresora: {cierre.diferencia_total:,} páginas")
            print(f"  Diferencia: {cierre.diferencia_total - total_consumo:,} páginas ({diferencia_porcentual:.1f}%)")
            
            if diferencia_porcentual > 10:
                print()
                print("  ⚠️  Hay una diferencia significativa entre el total de la impresora")
                print("     y la suma de usuarios. Posibles causas:")
                print("     - Impresiones sin autenticación")
                print("     - Usuarios borrados después del cierre")
                print("     - Trabajos de impresión del sistema")
        
        print()
        print("=" * 80)
        
    finally:
        db.close()


def main():
    if len(sys.argv) < 2:
        print("Uso: python ver_usuarios_cierre.py <cierre_id>")
        print()
        print("Ejemplo: python ver_usuarios_cierre.py 5")
        return
    
    cierre_id = int(sys.argv[1])
    ver_usuarios_cierre(cierre_id)


if __name__ == "__main__":
    main()
