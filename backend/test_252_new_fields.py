#!/usr/bin/env python3
"""
Test script to verify new fields are being saved for impresora 252
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db.database import get_db
from services.counter_service import CounterService

def test_252_fields():
    """Test that impresora 252 data includes new fields"""
    db = next(get_db())
    
    printer_id = 5  # Impresora 252
    
    print("=" * 80)
    print("TESTING IMPRESORA 252 - NEW FIELDS")
    print("=" * 80)
    
    # Trigger manual read
    print("\n1. Triggering manual read for impresora 252...")
    result = CounterService.read_printer_counters(db, printer_id)
    
    if not result['success']:
        print(f"❌ Error reading printer: {result.get('error')}")
        return
    
    print(f"✅ Read successful: {result['usuarios_count']} users")
    
    # Get latest user counters
    print("\n2. Fetching latest user counters...")
    users = CounterService.get_user_counters_latest(db, printer_id)
    
    if not users:
        print("❌ No user counters found")
        return
    
    print(f"✅ Found {len(users)} user counters")
    
    # Check first 3 users for new fields
    print("\n3. Checking new fields for first 3 users:")
    print("-" * 80)
    
    for i, user in enumerate(users[:3], 1):
        print(f"\nUser {i}: {user.nombre_usuario} ({user.codigo_usuario})")
        print(f"  Total: {user.total_paginas}")
        print(f"  Copiadora B/N: {user.copiadora_bn}")
        print(f"  Copiadora Hojas 2 Caras: {user.copiadora_hojas_2_caras}")
        print(f"  Copiadora Páginas Combinadas: {user.copiadora_paginas_combinadas}")
        print(f"  Impresora B/N: {user.impresora_bn}")
        print(f"  Impresora Hojas 2 Caras: {user.impresora_hojas_2_caras}")
        print(f"  Impresora Páginas Combinadas: {user.impresora_paginas_combinadas}")
    
    # Find DAVID SANDOVAL (1305)
    print("\n4. Looking for DAVID SANDOVAL (1305)...")
    david = next((u for u in users if u.codigo_usuario == '1305'), None)
    
    if david:
        print(f"\n✅ Found DAVID SANDOVAL:")
        print(f"  Código: {david.codigo_usuario}")
        print(f"  Nombre: {david.nombre_usuario}")
        print(f"  Total: {david.total_paginas}")
        print(f"  Copiadora B/N: {david.copiadora_bn}")
        print(f"  Copiadora Hojas 2 Caras: {david.copiadora_hojas_2_caras}")
        print(f"  Copiadora Páginas Combinadas: {david.copiadora_paginas_combinadas}")
        print(f"  Impresora B/N: {david.impresora_bn}")
        print(f"  Impresora Hojas 2 Caras: {david.impresora_hojas_2_caras}")
        print(f"  Impresora Páginas Combinadas: {david.impresora_paginas_combinadas}")
        print(f"  Escáner B/N: {david.escaner_bn}")
        print(f"  Escáner Color: {david.escaner_todo_color}")
        
        # Verify totals match
        expected_total = david.copiadora_bn + david.impresora_bn
        if david.total_paginas == expected_total:
            print(f"\n✅ Total matches: {david.total_paginas} = {david.copiadora_bn} + {david.impresora_bn}")
        else:
            print(f"\n⚠️  Total mismatch: {david.total_paginas} != {expected_total}")
    else:
        print("❌ DAVID SANDOVAL (1305) not found")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    test_252_fields()
