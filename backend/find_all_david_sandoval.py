#!/usr/bin/env python3
"""
Busca TODOS los usuarios llamados DAVID SANDOVAL en la web de la impresora
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parsear_contadores_usuario import get_all_user_counters

printer_ip = "192.168.91.252"

print("=" * 100)
print("🔍 BUSCANDO TODOS LOS 'DAVID SANDOVAL' EN LA WEB")
print("=" * 100)

print(f"\nImpresora: {printer_ip}")
print("\nObteniendo TODOS los usuarios...")

users = get_all_user_counters(printer_ip)

print(f"Total de usuarios: {len(users)}")

# Buscar todos los DAVID SANDOVAL
david_sandovals = []
for user in users:
    if "DAVID" in user['nombre_usuario'].upper() and "SANDOVAL" in user['nombre_usuario'].upper():
        david_sandovals.append(user)

print(f"\n{'='*100}")
print(f"USUARIOS ENCONTRADOS CON 'DAVID SANDOVAL': {len(david_sandovals)}")
print(f"{'='*100}")

for i, user in enumerate(david_sandovals, 1):
    print(f"\n{i}. Código: {user['codigo_usuario']}")
    print(f"   Nombre: {user['nombre_usuario']}")
    print(f"   Total: {user['total_paginas']}")
    print(f"   Copiadora B/N: {user['copiadora']['blanco_negro']}")
    print(f"   Impresora B/N: {user['impresora']['blanco_negro']}")
    print(f"   Escáner B/N: {user['escaner']['blanco_negro']}")

# Buscar usuario con código 1305
print(f"\n{'='*100}")
print(f"USUARIO CON CÓDIGO 1305:")
print(f"{'='*100}")

user_1305 = None
for user in users:
    if user['codigo_usuario'] == "1305":
        user_1305 = user
        break

if user_1305:
    print(f"\nCódigo: {user_1305['codigo_usuario']}")
    print(f"Nombre: {user_1305['nombre_usuario']}")
    print(f"Total: {user_1305['total_paginas']}")
    print(f"Copiadora B/N: {user_1305['copiadora']['blanco_negro']}")
    print(f"Impresora B/N: {user_1305['impresora']['blanco_negro']}")
    print(f"Escáner B/N: {user_1305['escaner']['blanco_negro']}")
else:
    print("\n❌ No se encontró usuario con código 1305")

# Buscar usuario con total = 72
print(f"\n{'='*100}")
print(f"USUARIOS CON TOTAL = 72:")
print(f"{'='*100}")

users_72 = [u for u in users if u['total_paginas'] == 72]
print(f"\nEncontrados: {len(users_72)}")

for user in users_72:
    print(f"\nCódigo: {user['codigo_usuario']}")
    print(f"Nombre: {user['nombre_usuario']}")
    print(f"Total: {user['total_paginas']}")
    print(f"Copiadora B/N: {user['copiadora']['blanco_negro']}")
    print(f"Impresora B/N: {user['impresora']['blanco_negro']}")

print(f"\n{'='*100}")
