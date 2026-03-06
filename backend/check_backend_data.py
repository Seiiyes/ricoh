#!/usr/bin/env python3
"""
Verifica los datos exactos que están en el backend
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import ContadorUsuario

# Usuarios a verificar
usuarios = ["0547", "0707", "2788", "4079"]

db = next(get_db())

print("=" * 80)
print("DATOS EN EL BACKEND")
print("=" * 80)

for codigo in usuarios:
    latest = db.query(ContadorUsuario)\
        .filter(ContadorUsuario.printer_id == 4, ContadorUsuario.codigo_usuario == codigo)\
        .order_by(ContadorUsuario.created_at.desc())\
        .first()
    
    if latest:
        print(f"\nUsuario: {codigo} - {latest.nombre_usuario}")
        print(f"  Fecha lectura: {latest.created_at}")
        print(f"  Total: {latest.total_paginas}")
        print(f"  Copiadora B/N: {latest.copiadora_bn}")
        print(f"  Impresora B/N: {latest.impresora_bn}")
        print(f"  Escáner B/N: {latest.escaner_bn}")
    else:
        print(f"\nUsuario: {codigo} - NO ENCONTRADO")

db.close()
