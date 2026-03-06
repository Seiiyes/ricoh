#!/usr/bin/env python3
"""
Test de Precisión de Contadores por Usuario
Compara los datos del backend con los datos directos de la web de la impresora
"""
import sys
import os
from datetime import datetime

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import Printer, ContadorUsuario
from parsear_contadores_usuario import get_all_user_counters
from parsear_contador_ecologico import get_all_eco_users

def test_printer_user_counters(printer_id: int):
    """
    Prueba la precisión de los contadores de usuario para una impresora
    
    Args:
        printer_id: ID de la impresora en la base de datos
    """
    print("=" * 100)
    print(f"🔍 TEST DE PRECISIÓN - CONTADORES POR USUARIO")
    print("=" * 100)
    
    # Obtener información de la impresora
    db = next(get_db())
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    
    if not printer:
        print(f"❌ ERROR: Impresora {printer_id} no encontrada en la base de datos")
        return
    
    print(f"\n📍 Impresora: {printer.hostname} ({printer.ip_address})")
    print(f"   Modelo: {printer.detected_model or 'N/A'}")
    print(f"   Serial: {printer.serial_number or 'N/A'}")
    print(f"   Empresa: {printer.empresa or 'N/A'}")
    print(f"   Contador Usuario: {'Sí' if printer.tiene_contador_usuario else 'No'}")
    print(f"   Contador Ecológico: {'Sí' if printer.usar_contador_ecologico else 'No'}")
    
    # Obtener datos directos de la web de la impresora
    print(f"\n📥 Obteniendo datos DIRECTOS de la web de la impresora...")
    try:
        if printer.usar_contador_ecologico:
            web_users = get_all_eco_users(printer.ip_address)
        else:
            web_users = get_all_user_counters(printer.ip_address)
        
        print(f"   ✅ {len(web_users)} usuarios obtenidos de la web")
    except Exception as e:
        print(f"   ❌ ERROR al obtener datos de la web: {e}")
        return
    
    # Obtener datos del backend (última lectura)
    print(f"\n💾 Obteniendo datos del BACKEND (última lectura)...")
    
    # Obtener el created_at más reciente
    latest_record = db.query(ContadorUsuario)\
        .filter(ContadorUsuario.printer_id == printer_id)\
        .order_by(ContadorUsuario.created_at.desc())\
        .first()
    
    if not latest_record:
        print(f"   ⚠️  No hay registros en el backend para esta impresora")
        backend_users = []
    else:
        latest_created_at = latest_record.created_at
        backend_users = db.query(ContadorUsuario)\
            .filter(
                ContadorUsuario.printer_id == printer_id,
                ContadorUsuario.created_at == latest_created_at
            )\
            .all()
        
        print(f"   ✅ {len(backend_users)} usuarios en el backend")
        print(f"   📅 Fecha de lectura: {latest_created_at}")
    
    # Comparar datos
    print(f"\n🔍 COMPARACIÓN DE DATOS")
    print("=" * 100)
    
    # Crear diccionarios para búsqueda rápida
    web_dict = {u['codigo_usuario']: u for u in web_users}
    backend_dict = {u.codigo_usuario: u for u in backend_users}
    
    # Encontrar usuarios en ambos lados
    all_codes = set(web_dict.keys()) | set(backend_dict.keys())
    
    discrepancies = []
    matches = 0
    
    for codigo in sorted(all_codes):
        web_user = web_dict.get(codigo)
        backend_user = backend_dict.get(codigo)
        
        if not web_user:
            discrepancies.append({
                'codigo': codigo,
                'issue': 'SOLO_EN_BACKEND',
                'backend_total': backend_user.total_paginas if backend_user else 0
            })
            continue
        
        if not backend_user:
            discrepancies.append({
                'codigo': codigo,
                'nombre': web_user['nombre_usuario'],
                'issue': 'SOLO_EN_WEB',
                'web_total': web_user['total_paginas']
            })
            continue
        
        # Comparar totales
        web_total = web_user['total_paginas']
        backend_total = backend_user.total_paginas
        
        if web_total != backend_total:
            discrepancies.append({
                'codigo': codigo,
                'nombre': web_user['nombre_usuario'],
                'issue': 'TOTAL_DIFERENTE',
                'web_total': web_total,
                'backend_total': backend_total,
                'diferencia': backend_total - web_total,
                'web_data': {
                    'copiadora_bn': web_user['copiadora']['blanco_negro'],
                    'copiadora_color': web_user['copiadora'].get('todo_color', 0),
                    'impresora_bn': web_user['impresora']['blanco_negro'],
                    'impresora_color': web_user['impresora'].get('color', 0),
                    'escaner_bn': web_user['escaner']['blanco_negro'],
                    'escaner_color': web_user['escaner'].get('todo_color', 0),
                },
                'backend_data': {
                    'copiadora_bn': backend_user.copiadora_bn,
                    'copiadora_color': backend_user.copiadora_todo_color,
                    'impresora_bn': backend_user.impresora_bn,
                    'impresora_color': backend_user.impresora_color,
                    'escaner_bn': backend_user.escaner_bn,
                    'escaner_color': backend_user.escaner_todo_color,
                }
            })
        else:
            matches += 1
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS:")
    print(f"   ✅ Usuarios coincidentes: {matches}")
    print(f"   ❌ Discrepancias encontradas: {len(discrepancies)}")
    
    if discrepancies:
        print(f"\n⚠️  DISCREPANCIAS DETALLADAS:")
        print("-" * 100)
        
        for i, disc in enumerate(discrepancies[:20], 1):  # Mostrar primeras 20
            print(f"\n{i}. Usuario: {disc.get('nombre', 'N/A')} (Código: {disc['codigo']})")
            print(f"   Problema: {disc['issue']}")
            
            if disc['issue'] == 'TOTAL_DIFERENTE':
                print(f"   Web Total: {disc['web_total']:,}")
                print(f"   Backend Total: {disc['backend_total']:,}")
                print(f"   Diferencia: {disc['diferencia']:+,}")
                
                print(f"\n   Desglose WEB:")
                print(f"      Copiadora B/N: {disc['web_data']['copiadora_bn']:,}")
                print(f"      Copiadora Color: {disc['web_data']['copiadora_color']:,}")
                print(f"      Impresora B/N: {disc['web_data']['impresora_bn']:,}")
                print(f"      Impresora Color: {disc['web_data']['impresora_color']:,}")
                print(f"      Escáner B/N: {disc['web_data']['escaner_bn']:,}")
                print(f"      Escáner Color: {disc['web_data']['escaner_color']:,}")
                
                print(f"\n   Desglose BACKEND:")
                print(f"      Copiadora B/N: {disc['backend_data']['copiadora_bn']:,}")
                print(f"      Copiadora Color: {disc['backend_data']['copiadora_color']:,}")
                print(f"      Impresora B/N: {disc['backend_data']['impresora_bn']:,}")
                print(f"      Impresora Color: {disc['backend_data']['impresora_color']:,}")
                print(f"      Escáner B/N: {disc['backend_data']['escaner_bn']:,}")
                print(f"      Escáner Color: {disc['backend_data']['escaner_color']:,}")
            
            elif disc['issue'] == 'SOLO_EN_WEB':
                print(f"   Web Total: {disc['web_total']:,}")
                print(f"   ⚠️  Este usuario NO está en el backend")
            
            elif disc['issue'] == 'SOLO_EN_BACKEND':
                print(f"   Backend Total: {disc['backend_total']:,}")
                print(f"   ⚠️  Este usuario NO está en la web")
        
        if len(discrepancies) > 20:
            print(f"\n... y {len(discrepancies) - 20} discrepancias más")
    
    # Resumen final
    print("\n" + "=" * 100)
    print("📋 RESUMEN")
    print("=" * 100)
    
    accuracy = (matches / len(all_codes) * 100) if all_codes else 0
    print(f"\n✅ Precisión: {accuracy:.1f}% ({matches}/{len(all_codes)} usuarios)")
    
    if accuracy < 100:
        print(f"\n⚠️  ATENCIÓN: Los datos del backend NO coinciden con la web de la impresora")
        print(f"   Se requiere investigación adicional del parser o del servicio de lectura")
    else:
        print(f"\n✅ PERFECTO: Todos los datos coinciden con la web de la impresora")
    
    db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_user_counters_accuracy.py <printer_id>")
        print("\nImpresoras disponibles:")
        db = next(get_db())
        printers = db.query(Printer).all()
        for p in printers:
            print(f"  {p.id}: {p.hostname} ({p.ip_address})")
        db.close()
        sys.exit(1)
    
    printer_id = int(sys.argv[1])
    test_printer_user_counters(printer_id)
