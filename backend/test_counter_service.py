#!/usr/bin/env python3
"""
Test del servicio de contadores
Prueba lectura y almacenamiento de contadores
"""
from services.counter_service import CounterService
from db.database import get_db

def test_single_printer():
    """Prueba lectura de una sola impresora"""
    print("=" * 80)
    print("🧪 TEST: Lectura de Contadores - Impresora Individual")
    print("=" * 80)
    
    printer_id = 4  # Impresora 192.168.91.251
    
    db = next(get_db())
    
    try:
        # 1. Leer contadores totales
        print(f"\n1. Leyendo contadores totales de impresora ID {printer_id}...")
        contador_total = CounterService.read_printer_counters(db, printer_id)
        
        if contador_total:
            print(f"   ✅ Contador total guardado:")
            print(f"      - ID: {contador_total.id}")
            print(f"      - Total páginas: {contador_total.total:,}")
            print(f"      - Copiadora: {contador_total.copiadora_bn + contador_total.copiadora_color:,}")
            print(f"      - Impresora: {contador_total.impresora_bn + contador_total.impresora_color:,}")
            print(f"      - Fecha lectura: {contador_total.fecha_lectura}")
        
        # 2. Leer contadores por usuario
        print(f"\n2. Leyendo contadores por usuario de impresora ID {printer_id}...")
        contadores_usuarios = CounterService.read_user_counters(db, printer_id)
        
        print(f"   ✅ {len(contadores_usuarios)} usuarios guardados")
        
        # Mostrar top 5 usuarios
        if contadores_usuarios:
            top_users = sorted(contadores_usuarios, key=lambda x: x.total_paginas, reverse=True)[:5]
            print(f"\n   📊 Top 5 usuarios con más impresiones:")
            for i, user in enumerate(top_users, 1):
                print(f"      {i}. {user.nombre_usuario} ({user.codigo_usuario}): {user.total_paginas:,} páginas")
        
        # 3. Obtener último contador
        print(f"\n3. Verificando último contador registrado...")
        ultimo = CounterService.get_latest_counter(db, printer_id)
        
        if ultimo:
            print(f"   ✅ Último contador:")
            print(f"      - Total: {ultimo.total:,}")
            print(f"      - Fecha: {ultimo.fecha_lectura}")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def test_all_printers():
    """Prueba lectura de todas las impresoras"""
    print("=" * 80)
    print("🧪 TEST: Lectura de Contadores - Todas las Impresoras")
    print("=" * 80)
    
    db = next(get_db())
    
    try:
        print("\nLeyendo contadores de todas las impresoras...")
        results = CounterService.read_all_printers(db)
        
        print(f"\n✅ Procesadas {len(results)} impresoras")
        
        for printer_id, result in results.items():
            print(f"\n{'=' * 80}")
            print(f"🖨️  Impresora ID {printer_id}: {result['hostname']} ({result['ip_address']})")
            print(f"{'=' * 80}")
            
            if result['success']:
                print(f"✅ Contador total guardado")
                if result['contador_total']:
                    print(f"   - Total páginas: {result['contador_total'].total:,}")
                
                if result['contadores_usuarios']:
                    print(f"✅ {len(result['contadores_usuarios'])} usuarios guardados")
                
                if result['error']:
                    print(f"⚠️  Advertencia: {result['error']}")
            else:
                print(f"❌ Error: {result['error']}")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETADO")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def test_monthly_close():
    """Prueba cierre mensual"""
    print("=" * 80)
    print("🧪 TEST: Cierre Mensual")
    print("=" * 80)
    
    printer_id = 4
    year = 2026
    month = 3  # Marzo
    
    db = next(get_db())
    
    try:
        print(f"\nRealizando cierre mensual para {year}-{month:02d}...")
        
        cierre = CounterService.close_month(
            db, 
            printer_id, 
            year, 
            month,
            cerrado_por="admin",
            notas="Cierre de prueba"
        )
        
        print(f"\n✅ Cierre mensual creado:")
        print(f"   - ID: {cierre.id}")
        print(f"   - Período: {cierre.anio}-{cierre.mes:02d}")
        print(f"   - Total páginas: {cierre.total_paginas:,}")
        print(f"   - Diferencia con mes anterior: {cierre.diferencia_total:,}")
        print(f"   - Fecha cierre: {cierre.fecha_cierre}")
        print(f"   - Cerrado por: {cierre.cerrado_por}")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == "single":
            test_single_printer()
        elif test_type == "all":
            test_all_printers()
        elif test_type == "close":
            test_monthly_close()
        else:
            print("Uso: python test_counter_service.py [single|all|close]")
    else:
        # Por defecto, ejecutar test de una sola impresora
        test_single_printer()
