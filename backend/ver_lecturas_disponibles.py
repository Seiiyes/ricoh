#!/usr/bin/env python3
"""
Script para ver las lecturas disponibles por fecha
Útil para saber qué cierres diarios se pueden crear
"""
import sys
import os
from datetime import datetime, date
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import ContadorImpresora, Printer


def ver_lecturas_por_fecha(db: Session, printer_id: int = None):
    """
    Muestra las lecturas agrupadas por fecha
    """
    print("=" * 80)
    print("📅 LECTURAS DISPONIBLES POR FECHA")
    print("=" * 80)
    print()
    
    # Query base
    query = db.query(
        ContadorImpresora.printer_id,
        cast(ContadorImpresora.fecha_lectura, Date).label('fecha'),
        func.count(ContadorImpresora.id).label('cantidad_lecturas'),
        func.min(ContadorImpresora.fecha_lectura).label('primera_lectura'),
        func.max(ContadorImpresora.fecha_lectura).label('ultima_lectura'),
        func.max(ContadorImpresora.total).label('contador_final')
    )
    
    if printer_id:
        query = query.filter(ContadorImpresora.printer_id == printer_id)
    
    # Agrupar por impresora y fecha
    lecturas = query.group_by(
        ContadorImpresora.printer_id,
        cast(ContadorImpresora.fecha_lectura, Date)
    ).order_by(
        ContadorImpresora.printer_id,
        cast(ContadorImpresora.fecha_lectura, Date).desc()
    ).all()
    
    if not lecturas:
        print("⚠️  No hay lecturas registradas")
        return
    
    # Obtener información de impresoras
    printers = {p.id: p for p in db.query(Printer).all()}
    
    # Agrupar por impresora
    current_printer = None
    for lectura in lecturas:
        if current_printer != lectura.printer_id:
            current_printer = lectura.printer_id
            printer = printers.get(lectura.printer_id)
            
            print()
            print("─" * 80)
            print(f"🖨️  Impresora {lectura.printer_id}: {printer.hostname if printer else 'Desconocida'}")
            print(f"   IP: {printer.ip_address if printer else 'N/A'}")
            print(f"   Ubicación: {printer.location if printer else 'N/A'}")
            print("─" * 80)
            print()
            print(f"{'Fecha':<12} {'Lecturas':<10} {'Primera':<20} {'Última':<20} {'Contador Final':<15}")
            print("─" * 80)
        
        fecha_str = lectura.fecha.strftime('%Y-%m-%d')
        primera_str = lectura.primera_lectura.strftime('%H:%M:%S')
        ultima_str = lectura.ultima_lectura.strftime('%H:%M:%S')
        
        print(f"{fecha_str:<12} {lectura.cantidad_lecturas:<10} {primera_str:<20} {ultima_str:<20} {lectura.contador_final:>15,}")
    
    print()
    print("=" * 80)


def ver_lecturas_mes_actual(db: Session, printer_id: int):
    """
    Muestra las lecturas del mes actual para una impresora
    """
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        print(f"❌ Impresora {printer_id} no encontrada")
        return
    
    print("=" * 80)
    print(f"📅 LECTURAS DEL MES ACTUAL - Impresora {printer_id}")
    print(f"   {printer.hostname} ({printer.ip_address})")
    print("=" * 80)
    print()
    
    # Obtener primer y último día del mes actual
    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    
    # Query
    lecturas = db.query(
        cast(ContadorImpresora.fecha_lectura, Date).label('fecha'),
        func.count(ContadorImpresora.id).label('cantidad'),
        func.min(ContadorImpresora.total).label('contador_min'),
        func.max(ContadorImpresora.total).label('contador_max')
    ).filter(
        ContadorImpresora.printer_id == printer_id,
        cast(ContadorImpresora.fecha_lectura, Date) >= primer_dia
    ).group_by(
        cast(ContadorImpresora.fecha_lectura, Date)
    ).order_by(
        cast(ContadorImpresora.fecha_lectura, Date)
    ).all()
    
    if not lecturas:
        print("⚠️  No hay lecturas en el mes actual")
        return
    
    print(f"{'Fecha':<12} {'Lecturas':<10} {'Contador Min':<15} {'Contador Max':<15} {'Diferencia':<12}")
    print("─" * 80)
    
    total_diferencia = 0
    for i, lectura in enumerate(lecturas):
        fecha_str = lectura.fecha.strftime('%Y-%m-%d')
        diferencia = lectura.contador_max - lectura.contador_min
        total_diferencia += diferencia
        
        print(f"{fecha_str:<12} {lectura.cantidad:<10} {lectura.contador_min:>15,} {lectura.contador_max:>15,} {diferencia:>12,}")
    
    print("─" * 80)
    print(f"{'TOTAL':<12} {len(lecturas):<10} {'':<15} {'':<15} {total_diferencia:>12,}")
    print()
    print("=" * 80)
    print()
    print("💡 Puedes crear cierres diarios para cualquiera de estas fechas")
    print()


def sugerir_cierres_diarios(db: Session, printer_id: int):
    """
    Sugiere qué cierres diarios se pueden crear
    """
    from db.models import CierreMensual
    
    printer = db.query(Printer).filter(Printer.id == printer_id).first()
    if not printer:
        print(f"❌ Impresora {printer_id} no encontrada")
        return
    
    print("=" * 80)
    print(f"💡 SUGERENCIAS DE CIERRES DIARIOS - Impresora {printer_id}")
    print(f"   {printer.hostname} ({printer.ip_address})")
    print("=" * 80)
    print()
    
    # Obtener fechas con lecturas
    fechas_con_lecturas = db.query(
        cast(ContadorImpresora.fecha_lectura, Date).label('fecha')
    ).filter(
        ContadorImpresora.printer_id == printer_id
    ).distinct().order_by(
        cast(ContadorImpresora.fecha_lectura, Date).desc()
    ).limit(30).all()
    
    # Obtener cierres diarios existentes
    cierres_existentes = db.query(
        CierreMensual.fecha_inicio
    ).filter(
        CierreMensual.printer_id == printer_id,
        CierreMensual.tipo_periodo == 'diario'
    ).all()
    
    fechas_cerradas = {c.fecha_inicio for c in cierres_existentes}
    
    print("Fechas disponibles para crear cierres diarios:")
    print()
    print(f"{'Fecha':<12} {'Estado':<20} {'Acción':<30}")
    print("─" * 80)
    
    disponibles = 0
    for (fecha,) in fechas_con_lecturas:
        if fecha in fechas_cerradas:
            estado = "✅ Ya cerrado"
            accion = "N/A"
        elif fecha >= date.today():
            estado = "⏳ Día actual/futuro"
            accion = "Esperar a que termine el día"
        else:
            estado = "📅 Disponible"
            accion = "Crear cierre diario"
            disponibles += 1
        
        fecha_str = fecha.strftime('%Y-%m-%d')
        print(f"{fecha_str:<12} {estado:<20} {accion:<30}")
    
    print("─" * 80)
    print(f"Total disponibles: {disponibles}")
    print()
    print("=" * 80)


def main():
    """Función principal"""
    db = next(get_db())
    
    try:
        import sys
        
        if len(sys.argv) > 1:
            printer_id = int(sys.argv[1])
            
            # Ver lecturas del mes actual
            ver_lecturas_mes_actual(db, printer_id)
            
            # Sugerir cierres diarios
            sugerir_cierres_diarios(db, printer_id)
        else:
            # Ver todas las lecturas
            ver_lecturas_por_fecha(db)
            
            print()
            print("💡 Uso: python ver_lecturas_disponibles.py [printer_id]")
            print("   Ejemplo: python ver_lecturas_disponibles.py 4")
            print()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
