#!/usr/bin/env python3
"""
Script de prueba para el cierre mensual con snapshot de usuarios
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from services.counter_service import CounterService
from db.models import CierreMensual, CierreMensualUsuario, Printer


def test_cierre_mensual():
    """Prueba el cierre mensual con snapshot de usuarios"""
    
    print("=" * 80)
    print("🧪 PRUEBA DE CIERRE MENSUAL CON SNAPSHOT DE USUARIOS")
    print("=" * 80)
    print()
    
    db = next(get_db())
    
    try:
        # 1. Listar impresoras disponibles
        print("📋 Impresoras disponibles:")
        print("-" * 80)
        printers = db.query(Printer).all()
        
        if not printers:
            print("❌ No hay impresoras registradas")
            return
        
        for p in printers:
            print(f"  ID: {p.id:3d} | IP: {p.ip_address:15s} | Hostname: {p.hostname or 'N/A'}")
        
        print()
        
        # 2. Seleccionar impresora para prueba
        printer_id = int(input("Ingrese ID de impresora para cerrar mes: "))
        
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            print(f"❌ Impresora {printer_id} no encontrada")
            return
        
        print(f"✅ Impresora seleccionada: {printer.hostname or printer.ip_address}")
        print()
        
        # 3. Mostrar cierres existentes
        print("📅 Cierres existentes:")
        print("-" * 80)
        cierres = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer_id
        ).order_by(CierreMensual.anio.desc(), CierreMensual.mes.desc()).all()
        
        if cierres:
            for c in cierres:
                print(f"  {c.anio}-{c.mes:02d} | Total: {c.total_paginas:,} | "
                      f"Diferencia: {c.diferencia_total:,} | "
                      f"Por: {c.cerrado_por or 'N/A'}")
        else:
            print("  (No hay cierres previos)")
        
        print()
        
        # 4. Solicitar datos del cierre
        fecha_actual = datetime.now()
        year = int(input(f"Año del cierre [{fecha_actual.year}]: ") or fecha_actual.year)
        month = int(input(f"Mes del cierre (1-12) [{fecha_actual.month}]: ") or fecha_actual.month)
        cerrado_por = input("Usuario que cierra [admin]: ") or "admin"
        notas = input("Notas (opcional): ") or None
        
        print()
        print("⏳ Procesando cierre mensual...")
        print()
        
        # 5. Ejecutar cierre
        cierre = CounterService.close_month(
            db=db,
            printer_id=printer_id,
            year=year,
            month=month,
            cerrado_por=cerrado_por,
            notas=notas
        )
        
        print("=" * 80)
        print("✅ CIERRE MENSUAL COMPLETADO")
        print("=" * 80)
        print()
        
        # 6. Mostrar resumen del cierre
        print("📊 RESUMEN DEL CIERRE:")
        print("-" * 80)
        print(f"ID del cierre:        {cierre.id}")
        print(f"Impresora:            {printer.hostname or printer.ip_address}")
        print(f"Período:              {cierre.anio}-{cierre.mes:02d}")
        print(f"Fecha de cierre:      {cierre.fecha_cierre.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Cerrado por:          {cierre.cerrado_por or 'N/A'}")
        print()
        
        print("📈 TOTALES ACUMULADOS:")
        print("-" * 80)
        print(f"Total páginas:        {cierre.total_paginas:,}")
        print(f"Total copiadora:      {cierre.total_copiadora:,}")
        print(f"Total impresora:      {cierre.total_impresora:,}")
        print(f"Total escáner:        {cierre.total_escaner:,}")
        print(f"Total fax:            {cierre.total_fax:,}")
        print()
        
        print("📉 CONSUMO DEL MES:")
        print("-" * 80)
        print(f"Diferencia total:     {cierre.diferencia_total:,}")
        print(f"Diferencia copiadora: {cierre.diferencia_copiadora:,}")
        print(f"Diferencia impresora: {cierre.diferencia_impresora:,}")
        print(f"Diferencia escáner:   {cierre.diferencia_escaner:,}")
        print(f"Diferencia fax:       {cierre.diferencia_fax:,}")
        print()
        
        # 7. Mostrar snapshot de usuarios
        usuarios = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre.id
        ).order_by(CierreMensualUsuario.consumo_total.desc()).all()
        
        print("👥 SNAPSHOT DE USUARIOS:")
        print("-" * 80)
        print(f"Total usuarios:       {len(usuarios)}")
        print()
        
        if usuarios:
            print("Top 10 usuarios por consumo:")
            print()
            print(f"{'Código':<10} {'Nombre':<30} {'Consumo':<12} {'Copiadora':<12} {'Impresora':<12}")
            print("-" * 80)
            
            for u in usuarios[:10]:
                print(f"{u.codigo_usuario:<10} {u.nombre_usuario:<30} "
                      f"{u.consumo_total:>10,}  {u.consumo_copiadora:>10,}  "
                      f"{u.consumo_impresora:>10,}")
        
        print()
        
        # 8. Validación de integridad
        suma_consumos = sum(u.consumo_total for u in usuarios)
        diferencia_validacion = abs(suma_consumos - cierre.diferencia_total)
        porcentaje_diferencia = (diferencia_validacion / cierre.diferencia_total * 100) if cierre.diferencia_total > 0 else 0
        
        print("🔍 VALIDACIÓN DE INTEGRIDAD:")
        print("-" * 80)
        print(f"Consumo total (impresora): {cierre.diferencia_total:,}")
        print(f"Suma consumos (usuarios):  {suma_consumos:,}")
        print(f"Diferencia:                {diferencia_validacion:,} ({porcentaje_diferencia:.2f}%)")
        
        if porcentaje_diferencia <= 10:
            print("✅ Validación OK (diferencia <= 10%)")
        else:
            print("⚠️  Advertencia: diferencia > 10%")
        
        print()
        
        # 9. Hash de verificación
        if cierre.hash_verificacion:
            print("🔐 HASH DE VERIFICACIÓN:")
            print("-" * 80)
            print(f"Hash: {cierre.hash_verificacion}")
            print()
        
        # 10. Notas
        if cierre.notas:
            print("📝 NOTAS:")
            print("-" * 80)
            print(cierre.notas)
            print()
        
        print("=" * 80)
        print("✅ Prueba completada exitosamente")
        print("=" * 80)
        
    except ValueError as e:
        print()
        print("=" * 80)
        print("❌ ERROR DE VALIDACIÓN")
        print("=" * 80)
        print()
        print(str(e))
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR INESPERADO")
        print("=" * 80)
        print()
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {e}")
        print()
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    test_cierre_mensual()
