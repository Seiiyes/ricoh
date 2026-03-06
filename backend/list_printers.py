#!/usr/bin/env python3
"""
Lista todas las impresoras en la base de datos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import Printer

db = next(get_db())

print("=" * 80)
print("IMPRESORAS EN LA BASE DE DATOS")
print("=" * 80)

printers = db.query(Printer).all()

for p in printers:
    print(f"\nID: {p.id}")
    print(f"  Hostname: {p.hostname}")
    print(f"  IP: {p.ip_address}")
    print(f"  Empresa: {p.empresa or 'N/A'}")
    print(f"  Contador Usuario: {'Sí' if p.tiene_contador_usuario else 'No'}")
    print(f"  Contador Ecológico: {'Sí' if p.usar_contador_ecologico else 'No'}")

db.close()
