#!/usr/bin/env python3
"""
Verificar coherencia de contadores con la interfaz web
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsear_contadores import get_printer_counters
from db.database import get_db
from db.models import Printer, ContadorImpresora

print("=" * 80)
print("🔍 VERIFICACIÓN DE COHERENCIA DE CONTADORES")
print("=" * 80)

db = next(get_db())

try:
    # Obtener todas las impresoras
    printers = db.query(Printer).all()
    
    for printer in printers:
        print(f"\n{'=' * 80}")
        print(f"🖨️  Impresora ID {printer.id}: {printer.hostname}")
        print(f"    IP: {printer.ip_address}")
        print(f"{'=' * 80}")
        
        # Leer contador directamente de la impresora
        print("\n📡 Leyendo directamente de la impresora...")
        try:
            counters = get_printer_counters(printer.ip_address)
            
            print(f"\n✅ Datos de la interfaz web:")
            print(f"   Total: {counters['total']:,} páginas")
            print(f"   Copiadora B/N: {counters['copiadora']['blanco_negro']:,}")
            print(f"   Copiadora Color: {counters['copiadora']['color']:,}")
            print(f"   Copiadora Color Personalizado: {counters['copiadora']['color_personalizado']:,}")
            print(f"   Copiadora Dos Colores: {counters['copiadora']['dos_colores']:,}")
            print(f"   Impresora B/N: {counters['impresora']['blanco_negro']:,}")
            print(f"   Impresora Color: {counters['impresora']['color']:,}")
            print(f"   Impresora Color Personalizado: {counters['impresora']['color_personalizado']:,}")
            print(f"   Impresora Dos Colores: {counters['impresora']['dos_colores']:,}")
            print(f"   Fax B/N: {counters['fax']['blanco_negro']:,}")
            print(f"   Escáner B/N: {counters['envio_escaner']['blanco_negro']:,}")
            print(f"   Escáner Color: {counters['envio_escaner']['color']:,}")
            
            # Calcular totales correctamente
            # En impresoras a color, el color ya incluye B/N, NO se suman
            # El total de cada función es el máximo entre B/N y los tipos de color
            total_copiadora = max(
                counters['copiadora']['blanco_negro'],
                counters['copiadora']['color'],
                counters['copiadora']['color_personalizado'],
                counters['copiadora']['dos_colores']
            )
            
            total_impresora = max(
                counters['impresora']['blanco_negro'],
                counters['impresora']['color'],
                counters['impresora']['color_personalizado'],
                counters['impresora']['dos_colores']
            )
            
            print(f"\n📊 Totales calculados:")
            print(f"   Total Copiadora: {total_copiadora:,}")
            print(f"   Total Impresora: {total_impresora:,}")
            print(f"   Total (Cop+Imp): {total_copiadora + total_impresora:,}")
            
            # Verificar coherencia
            if counters['total'] == total_copiadora + total_impresora:
                print(f"   ✅ COHERENTE: Total = Copiadora + Impresora")
            elif counters['total'] > total_copiadora + total_impresora:
                diferencia = counters['total'] - (total_copiadora + total_impresora)
                print(f"   ℹ️  Total es mayor por {diferencia:,} páginas")
                print(f"       (puede incluir fax, escáner u otras funciones)")
            else:
                print(f"   ⚠️  INCONSISTENCIA: Total < Copiadora + Impresora")
            
            # Obtener último contador de la base de datos
            ultimo_contador = db.query(ContadorImpresora).filter(
                ContadorImpresora.printer_id == printer.id
            ).order_by(ContadorImpresora.fecha_lectura.desc()).first()
            
            if ultimo_contador:
                print(f"\n💾 Último contador en base de datos:")
                print(f"   Total: {ultimo_contador.total:,} páginas")
                print(f"   Fecha: {ultimo_contador.fecha_lectura}")
                
                # Comparar
                if ultimo_contador.total == counters['total']:
                    print(f"   ✅ COINCIDE con la interfaz web")
                else:
                    diferencia = abs(ultimo_contador.total - counters['total'])
                    print(f"   ⚠️  DIFERENCIA: {diferencia:,} páginas")
                    if counters['total'] > ultimo_contador.total:
                        print(f"       La impresora tiene {diferencia:,} páginas más (uso reciente)")
                    else:
                        print(f"       ⚠️  ERROR: DB tiene más páginas que la impresora")
            
        except Exception as e:
            print(f"   ❌ Error al leer impresora: {e}")
    
finally:
    db.close()

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
print("\n💡 NOTAS:")
print("   - El 'Total' puede ser mayor que Copiadora+Impresora")
print("   - Esto es normal si incluye fax, escáner u otras funciones")
print("   - Lo importante es que los valores coincidan con la interfaz web")
print("=" * 80)
