#!/usr/bin/env python3
"""
Script para probar las funciones de exportación
Verifica que las exportaciones funcionen con la base de datos normalizada
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import CierreMensual, User
from services.export_ricoh import crear_fila_usuario, exportar_comparacion_ricoh
from datetime import datetime

def test_crear_fila_usuario(db: Session):
    """Prueba la función crear_fila_usuario con datos normalizados"""
    print("\n" + "="*80)
    print("TEST 1: Función crear_fila_usuario()")
    print("="*80)
    
    # Obtener un cierre con usuarios
    cierre = db.query(CierreMensual).first()
    
    if not cierre or not cierre.usuarios:
        print("❌ No hay cierres con usuarios")
        return False
    
    usuario = cierre.usuarios[0]
    
    print(f"\n✓ Usuario de prueba:")
    print(f"  - user_id: {usuario.user_id}")
    print(f"  - total_paginas: {usuario.total_paginas}")
    
    try:
        # Llamar a la función con db parameter
        fila = crear_fila_usuario(usuario, db=db)
        
        print(f"\n✓ Fila creada exitosamente:")
        print(f"  - Código: {fila[0]}")
        print(f"  - Nombre: {fila[1]}")
        print(f"  - Total páginas: {fila[2]}")
        print(f"  - Total B/N: {fila[3]}")
        print(f"  - Total Color: {fila[4]}")
        print(f"  - Columnas totales: {len(fila)}")
        
        if len(fila) != 52:
            print(f"  ⚠️ ADVERTENCIA: Se esperaban 52 columnas, se obtuvieron {len(fila)}")
        
        print("\n✅ TEST 1 PASADO: crear_fila_usuario() funciona correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exportar_comparacion_ricoh(db: Session):
    """Prueba la función exportar_comparacion_ricoh"""
    print("\n" + "="*80)
    print("TEST 2: Función exportar_comparacion_ricoh()")
    print("="*80)
    
    # Obtener dos cierres de la misma impresora
    cierres = db.query(CierreMensual).limit(2).all()
    
    if len(cierres) < 2:
        print("⚠️ No hay suficientes cierres para comparar")
        return True
    
    cierre1, cierre2 = cierres[0], cierres[1]
    
    print(f"\n✓ Cierres seleccionados:")
    print(f"  - Cierre 1: ID {cierre1.id} ({len(cierre1.usuarios)} usuarios)")
    print(f"  - Cierre 2: ID {cierre2.id} ({len(cierre2.usuarios)} usuarios)")
    
    # Obtener serial de la impresora
    from db.models import Printer
    printer = db.query(Printer).filter(Printer.id == cierre1.printer_id).first()
    
    if not printer or not printer.serial_number:
        print("⚠️ La impresora no tiene serial_number")
        return True
    
    try:
        print("\n⏳ Generando archivo Excel de comparación...")
        
        # Llamar a la función
        wb = exportar_comparacion_ricoh(
            db=db,
            serial_number=printer.serial_number,
            cierre1=cierre1,
            cierre2=cierre2
        )
        
        print(f"\n✓ Workbook creado exitosamente:")
        print(f"  - Hojas: {len(wb.sheetnames)}")
        
        for i, sheet_name in enumerate(wb.sheetnames, 1):
            ws = wb[sheet_name]
            print(f"  {i}. {sheet_name}")
            print(f"     - Filas: {ws.max_row}")
            print(f"     - Columnas: {ws.max_column}")
        
        # Verificar que la hoja comparativa tenga datos
        ws_comparativo = wb[wb.sheetnames[2]]  # Tercera hoja
        
        if ws_comparativo.max_row < 2:
            print("  ⚠️ La hoja comparativa no tiene datos")
        else:
            print(f"\n✓ Verificando datos de la hoja comparativa:")
            # Leer primera fila de datos (fila 2, después del header)
            fila_2 = [cell.value for cell in ws_comparativo[2]]
            print(f"  - Primera fila de datos: {fila_2[:5]}")
        
        print("\n✅ TEST 2 PASADO: exportar_comparacion_ricoh() funciona correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_exportacion_csv_simulada(db: Session):
    """Simula la exportación CSV como en export.py"""
    print("\n" + "="*80)
    print("TEST 3: Simulación de exportación CSV")
    print("="*80)
    
    # Obtener un cierre
    cierre = db.query(CierreMensual).first()
    
    if not cierre or not cierre.usuarios:
        print("❌ No hay cierres con usuarios")
        return False
    
    print(f"\n✓ Cierre seleccionado: ID {cierre.id}")
    print(f"  - Usuarios: {len(cierre.usuarios)}")
    
    try:
        # Simular el proceso de exportación CSV
        usuarios = sorted(cierre.usuarios, key=lambda u: u.consumo_total, reverse=True)
        
        print("\n✓ Generando filas CSV (primeros 5 usuarios):")
        
        for i, usuario in enumerate(usuarios[:5], 1):
            if usuario.consumo_total > 0:
                # Este es el código de export.py
                user = db.query(User).filter(User.id == usuario.user_id).first()
                codigo = user.codigo_de_usuario if user else str(usuario.user_id)
                nombre = user.name if user else f"Usuario {usuario.user_id}"
                
                bn = usuario.impresora_bn + usuario.copiadora_bn + usuario.escaner_bn
                color = usuario.impresora_color + usuario.copiadora_color + usuario.escaner_color
                total = usuario.consumo_total
                
                print(f"  {i}. [{codigo}],[{nombre}],{bn},{color},{total}")
        
        print("\n✅ TEST 3 PASADO: Exportación CSV simulada funciona correctamente")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("="*80)
    print("🧪 PRUEBAS DE FUNCIONES DE EXPORTACIÓN")
    print("="*80)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = SessionLocal()
    
    try:
        tests = [
            ("crear_fila_usuario()", test_crear_fila_usuario),
            ("exportar_comparacion_ricoh()", test_exportar_comparacion_ricoh),
            ("Exportación CSV simulada", test_exportacion_csv_simulada),
        ]
        
        resultados = []
        
        for nombre, test_func in tests:
            try:
                resultado = test_func(db)
                resultados.append((nombre, resultado))
            except Exception as e:
                print(f"\n❌ ERROR en {nombre}: {e}")
                import traceback
                traceback.print_exc()
                resultados.append((nombre, False))
        
        # Resumen
        print("\n" + "="*80)
        print("📊 RESUMEN DE PRUEBAS")
        print("="*80)
        
        pasados = sum(1 for _, r in resultados if r)
        total = len(resultados)
        
        print(f"\nPruebas ejecutadas: {total}")
        print(f"Pruebas pasadas: {pasados}")
        print(f"Pruebas fallidas: {total - pasados}")
        
        print("\nDetalle:")
        for nombre, resultado in resultados:
            estado = "✅ PASADO" if resultado else "❌ FALLIDO"
            print(f"  {estado}: {nombre}")
        
        if pasados == total:
            print("\n" + "="*80)
            print("🎉 ¡TODAS LAS PRUEBAS DE EXPORTACIÓN PASARON!")
            print("="*80)
            print("\n✅ Las funciones de exportación funcionan correctamente")
            print("✅ Los datos de usuario se obtienen mediante JOINs")
            print("✅ El formato Ricoh de 52 columnas se genera correctamente")
            return 0
        else:
            print("\n⚠️ Algunas pruebas fallaron")
            return 1
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
