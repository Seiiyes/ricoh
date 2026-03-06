#!/usr/bin/env python3
"""
Verifica específicamente el usuario DAVID SANDOVAL en impresora 252
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import ContadorUsuario
from parsear_contadores_usuario import get_all_user_counters

printer_ip = "192.168.91.252"
printer_id = 5
target_codigo = "1305"

print("=" * 100)
print("🔍 VERIFICACIÓN ESPECÍFICA: DAVID SANDOVAL (1305)")
print("=" * 100)

# 1. Obtener datos DIRECTOS de la web
print(f"\n1. Obteniendo datos DIRECTOS de la web de la impresora {printer_ip}...")
try:
    web_users = get_all_user_counters(printer_ip)
    web_user = None
    for user in web_users:
        if user['codigo_usuario'] == target_codigo:
            web_user = user
            break
    
    if web_user:
        print(f"   ✅ Usuario encontrado en la web")
        print(f"   Código: {web_user['codigo_usuario']}")
        print(f"   Nombre: {web_user['nombre_usuario']}")
        print(f"   Total: {web_user['total_paginas']}")
        print(f"   Copiadora B/N: {web_user['copiadora']['blanco_negro']}")
        print(f"   Impresora B/N: {web_user['impresora']['blanco_negro']}")
        print(f"   Escáner B/N: {web_user['escaner']['blanco_negro']}")
    else:
        print(f"   ❌ Usuario {target_codigo} NO encontrado en la web")
        print(f"   Total de usuarios en la web: {len(web_users)}")
        print(f"\n   Usuarios encontrados:")
        for user in web_users[:10]:
            print(f"      {user['codigo_usuario']} - {user['nombre_usuario']}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    web_user = None

# 2. Obtener datos del BACKEND
print(f"\n2. Obteniendo datos del BACKEND...")
db = next(get_db())

backend_user = db.query(ContadorUsuario)\
    .filter(ContadorUsuario.printer_id == printer_id, ContadorUsuario.codigo_usuario == target_codigo)\
    .order_by(ContadorUsuario.created_at.desc())\
    .first()

if backend_user:
    print(f"   ✅ Usuario encontrado en el backend")
    print(f"   Código: {backend_user.codigo_usuario}")
    print(f"   Nombre: {backend_user.nombre_usuario}")
    print(f"   Fecha lectura: {backend_user.created_at}")
    print(f"   Total: {backend_user.total_paginas}")
    print(f"   Copiadora B/N: {backend_user.copiadora_bn}")
    print(f"   Impresora B/N: {backend_user.impresora_bn}")
    print(f"   Escáner B/N: {backend_user.escaner_bn}")
else:
    print(f"   ❌ Usuario {target_codigo} NO encontrado en el backend")

# 3. Comparar
print(f"\n3. COMPARACIÓN:")
print("=" * 100)

if web_user and backend_user:
    print(f"\n{'Campo':<20} {'Web':<15} {'Backend':<15} {'Diferencia':<15}")
    print("-" * 100)
    print(f"{'Total':<20} {web_user['total_paginas']:<15} {backend_user.total_paginas:<15} {backend_user.total_paginas - web_user['total_paginas']:<15}")
    print(f"{'Copiadora B/N':<20} {web_user['copiadora']['blanco_negro']:<15} {backend_user.copiadora_bn:<15} {backend_user.copiadora_bn - web_user['copiadora']['blanco_negro']:<15}")
    print(f"{'Impresora B/N':<20} {web_user['impresora']['blanco_negro']:<15} {backend_user.impresora_bn:<15} {backend_user.impresora_bn - web_user['impresora']['blanco_negro']:<15}")
    print(f"{'Escáner B/N':<20} {web_user['escaner']['blanco_negro']:<15} {backend_user.escaner_bn:<15} {backend_user.escaner_bn - web_user['escaner']['blanco_negro']:<15}")
    
    if web_user['total_paginas'] == backend_user.total_paginas:
        print(f"\n✅ Los datos COINCIDEN perfectamente")
    else:
        print(f"\n❌ Los datos NO COINCIDEN")
        print(f"\n⚠️  PROBLEMA IDENTIFICADO: El parser NO está leyendo correctamente los datos")
elif not web_user:
    print(f"\n❌ Usuario {target_codigo} no existe en la web de la impresora")
    print(f"   Posiblemente el código de usuario es diferente")
elif not backend_user:
    print(f"\n❌ Usuario {target_codigo} no existe en el backend")
    print(f"   Necesita hacer una lectura manual")

db.close()

print("\n" + "=" * 100)
