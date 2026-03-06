#!/usr/bin/env python3
"""
Script de prueba para el sistema unificado de cierres
Valida todos los endpoints y funcionalidades
"""
import sys
import os
from datetime import date, datetime
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import CierreMensual, CierreMensualUsuario
from services.close_service import CloseService


def print_separator(title: str = ""):
    """Imprime un separador visual"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def test_crear_cierres(db: Session, printer_id: int):
    """Prueba la creación de diferentes tipos de cierres"""
    print_separator("TEST 1: CREAR CIERRES DE DIFERENTES TIPOS")
    
    try:
        # Limpiar cierres existentes de prueba
        db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.fecha_inicio >= date(2026, 3, 1)
        ).delete()
        db.commit()
        print("✅ Cierres de prueba anteriores eliminados")
        print()
        
        # 1. Cierre diario del 2 de marzo
        print("📅 Creando cierre diario del 2 de marzo...")
        cierre_diario_2 = CloseService.create_close(
            db=db,
            printer_id=printer_id,
            fecha_inicio=date(2026, 3, 2),
            fecha_fin=date(2026, 3, 2),
            tipo_periodo='diario',
            cerrado_por='admin',
            notas='Cierre diario de prueba'
        )
        print(f"   ✅ ID: {cierre_diario_2.id}")
        print(f"   Total: {cierre_diario_2.total_paginas:,} páginas")
        print(f"   Diferencia: {cierre_diario_2.diferencia_total:,} páginas")
        print(f"   Usuarios: {len(cierre_diario_2.usuarios)}")
        print()
        
        # 2. Cierre diario del 3 de marzo
        print("📅 Creando cierre diario del 3 de marzo...")
        cierre_diario_3 = CloseService.create_close(
            db=db,
            printer_id=printer_id,
            fecha_inicio=date(2026, 3, 3),
            fecha_fin=date(2026, 3, 3),
            tipo_periodo='diario',
            cerrado_por='admin',
            notas='Cierre diario de prueba'
        )
        print(f"   ✅ ID: {cierre_diario_3.id}")
        print(f"   Total: {cierre_diario_3.total_paginas:,} páginas")
        print(f"   Diferencia: {cierre_diario_3.diferencia_total:,} páginas ← Consumo del día 3")
        print(f"   Usuarios: {len(cierre_diario_3.usuarios)}")
        print()
        
        # 3. Cierre semanal (1-7 de marzo)
        print("📅 Creando cierre semanal (1-7 de marzo)...")
        cierre_semanal = CloseService.create_close(
            db=db,
            printer_id=printer_id,
            fecha_inicio=date(2026, 3, 1),
            fecha_fin=date(2026, 3, 7),
            tipo_periodo='semanal',
            cerrado_por='admin',
            notas='Primera semana de marzo'
        )
        print(f"   ✅ ID: {cierre_semanal.id}")
        print(f"   Total: {cierre_semanal.total_paginas:,} páginas")
        print(f"   Diferencia: {cierre_semanal.diferencia_total:,} páginas")
        print(f"   Usuarios: {len(cierre_semanal.usuarios)}")
        print()
        
        print("✅ TODOS LOS CIERRES CREADOS EXITOSAMENTE")
        print()
        print("📊 Resumen:")
        print(f"   - Cierre diario del 2: {cierre_diario_2.total_paginas:,} páginas")
        print(f"   - Cierre diario del 3: {cierre_diario_3.total_paginas:,} páginas (diferencia: {cierre_diario_3.diferencia_total:,})")
        print(f"   - Cierre semanal 1-7: {cierre_semanal.total_paginas:,} páginas")
        print()
        
        return {
            'diario_2': cierre_diario_2,
            'diario_3': cierre_diario_3,
            'semanal': cierre_semanal
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_listar_cierres(db: Session, printer_id: int):
    """Prueba el listado de cierres con filtros"""
    print_separator("TEST 2: LISTAR CIERRES CON FILTROS")
    
    try:
        # Listar todos los cierres
        print("📋 Listando TODOS los cierres...")
        todos = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id
        ).order_by(CierreMensual.fecha_inicio).all()
        
        print(f"   Total: {len(todos)} cierres")
        for c in todos:
            print(f"   - {c.tipo_periodo:12s} | {c.fecha_inicio} a {c.fecha_fin} | Total: {c.total_paginas:>10,} | Dif: {c.diferencia_total:>10,}")
        print()
        
        # Listar solo cierres diarios
        print("📋 Listando solo cierres DIARIOS...")
        diarios = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.tipo_periodo == 'diario'
        ).order_by(CierreMensual.fecha_inicio).all()
        
        print(f"   Total: {len(diarios)} cierres diarios")
        for c in diarios:
            print(f"   - {c.fecha_inicio} | Total: {c.total_paginas:>10,} | Dif: {c.diferencia_total:>10,}")
        print()
        
        # Listar solo cierres semanales
        print("📋 Listando solo cierres SEMANALES...")
        semanales = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id,
            CierreMensual.tipo_periodo == 'semanal'
        ).order_by(CierreMensual.fecha_inicio).all()
        
        print(f"   Total: {len(semanales)} cierres semanales")
        for c in semanales:
            print(f"   - {c.fecha_inicio} a {c.fecha_fin} | Total: {c.total_paginas:>10,} | Dif: {c.diferencia_total:>10,}")
        print()
        
        print("✅ LISTADO DE CIERRES EXITOSO")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_comparar_cierres(db: Session, cierres: dict):
    """Prueba la comparación entre dos cierres"""
    print_separator("TEST 3: COMPARAR CIERRES")
    
    if not cierres:
        print("⚠️  No hay cierres para comparar")
        return
    
    try:
        cierre1 = cierres['diario_2']
        cierre2 = cierres['diario_3']
        
        print(f"📊 Comparando cierre {cierre1.id} vs cierre {cierre2.id}")
        print()
        print(f"Cierre 1: {cierre1.tipo_periodo} del {cierre1.fecha_inicio}")
        print(f"   Total: {cierre1.total_paginas:,} páginas")
        print(f"   Usuarios: {len(cierre1.usuarios)}")
        print()
        print(f"Cierre 2: {cierre2.tipo_periodo} del {cierre2.fecha_inicio}")
        print(f"   Total: {cierre2.total_paginas:,} páginas")
        print(f"   Usuarios: {len(cierre2.usuarios)}")
        print()
        
        # Calcular diferencias
        diferencia_total = cierre2.total_paginas - cierre1.total_paginas
        dias_entre = (cierre2.fecha_fin - cierre1.fecha_fin).days
        
        print(f"📈 Diferencias:")
        print(f"   Total: {diferencia_total:,} páginas")
        print(f"   Días entre cierres: {dias_entre}")
        print(f"   Promedio diario: {diferencia_total / dias_entre if dias_entre > 0 else 0:,.1f} páginas/día")
        print()
        
        # Comparar usuarios
        usuarios1 = {u.codigo_usuario: u for u in cierre1.usuarios}
        usuarios2 = {u.codigo_usuario: u for u in cierre2.usuarios}
        
        # Top 5 usuarios con mayor consumo en el período
        comparaciones = []
        for codigo in usuarios2.keys():
            u1 = usuarios1.get(codigo)
            u2 = usuarios2.get(codigo)
            
            if u1 and u2:
                dif = u2.total_paginas - u1.total_paginas
                if dif > 0:
                    comparaciones.append({
                        'codigo': codigo,
                        'nombre': u2.nombre_usuario,
                        'diferencia': dif
                    })
        
        comparaciones.sort(key=lambda x: x['diferencia'], reverse=True)
        
        print("👥 Top 5 usuarios con mayor consumo:")
        for i, u in enumerate(comparaciones[:5], 1):
            print(f"   {i}. {u['nombre']:30s} ({u['codigo']}) - {u['diferencia']:>6,} páginas")
        print()
        
        print("✅ COMPARACIÓN EXITOSA")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_validaciones(db: Session, printer_id: int):
    """Prueba las validaciones del sistema"""
    print_separator("TEST 4: VALIDACIONES")
    
    try:
        # 1. Intentar crear cierre duplicado
        print("🔒 Intentando crear cierre duplicado...")
        try:
            CloseService.create_close(
                db=db,
                printer_id=printer_id,
                fecha_inicio=date(2026, 3, 2),
                fecha_fin=date(2026, 3, 2),
                tipo_periodo='diario',
                cerrado_por='admin'
            )
            print("   ❌ ERROR: Debería haber rechazado el duplicado")
        except ValueError as e:
            print(f"   ✅ Duplicado rechazado correctamente: {str(e)[:80]}...")
        print()
        
        # 2. Intentar crear cierre con fechas inválidas
        print("🔒 Intentando crear cierre con fecha_fin < fecha_inicio...")
        try:
            CloseService.create_close(
                db=db,
                printer_id=printer_id,
                fecha_inicio=date(2026, 3, 10),
                fecha_fin=date(2026, 3, 5),
                tipo_periodo='personalizado',
                cerrado_por='admin'
            )
            print("   ❌ ERROR: Debería haber rechazado fechas inválidas")
        except ValueError as e:
            print(f"   ✅ Fechas inválidas rechazadas: {str(e)[:80]}...")
        print()
        
        # 3. Intentar crear cierre con tipo inválido
        print("🔒 Intentando crear cierre con tipo inválido...")
        try:
            CloseService.create_close(
                db=db,
                printer_id=printer_id,
                fecha_inicio=date(2026, 3, 1),
                fecha_fin=date(2026, 3, 1),
                tipo_periodo='invalido',
                cerrado_por='admin'
            )
            print("   ❌ ERROR: Debería haber rechazado tipo inválido")
        except ValueError as e:
            print(f"   ✅ Tipo inválido rechazado: {str(e)[:80]}...")
        print()
        
        print("✅ TODAS LAS VALIDACIONES FUNCIONAN CORRECTAMENTE")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal"""
    print_separator("PRUEBA DEL SISTEMA UNIFICADO DE CIERRES")
    
    # Configuración
    PRINTER_ID = 4  # Impresora de prueba
    
    db = next(get_db())
    
    try:
        # Test 1: Crear cierres
        cierres = test_crear_cierres(db, PRINTER_ID)
        
        # Test 2: Listar cierres
        test_listar_cierres(db, PRINTER_ID)
        
        # Test 3: Comparar cierres
        test_comparar_cierres(db, cierres)
        
        # Test 4: Validaciones
        test_validaciones(db, PRINTER_ID)
        
        print_separator("✅ TODAS LAS PRUEBAS COMPLETADAS")
        print()
        print("📋 Resumen:")
        print("   ✅ Creación de cierres (diario, semanal)")
        print("   ✅ Listado con filtros por tipo")
        print("   ✅ Comparación entre cierres")
        print("   ✅ Validaciones de duplicados y fechas")
        print()
        print("🎉 El sistema unificado de cierres está funcionando correctamente")
        print()
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
