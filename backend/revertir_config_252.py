#!/usr/bin/env python3
"""
Revertir configuración de impresora 252
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import Printer

PRINTER_IP = "192.168.91.252"

print("=" * 80)
print("🔧 REVERTIR CONFIGURACIÓN IMPRESORA 252")
print("=" * 80)

db = next(get_db())

try:
    printer = db.query(Printer).filter(Printer.ip_address == PRINTER_IP).first()
    
    if not printer:
        print(f"❌ Impresora {PRINTER_IP} no encontrada")
        sys.exit(1)
    
    print(f"\n📋 Configuración actual:")
    print(f"   tiene_contador_usuario: {printer.tiene_contador_usuario}")
    print(f"   usar_contador_ecologico: {printer.usar_contador_ecologico}")
    
    # Revertir a configuración correcta
    printer.tiene_contador_usuario = True
    printer.usar_contador_ecologico = False
    
    db.commit()
    db.refresh(printer)
    
    print(f"\n✅ Configuración revertida:")
    print(f"   tiene_contador_usuario: {printer.tiene_contador_usuario}")
    print(f"   usar_contador_ecologico: {printer.usar_contador_ecologico}")
    
finally:
    db.close()

print("\n" + "=" * 80)
print("✅ REVERTIDO")
print("=" * 80)
