"""
Script para listar todas las impresoras en la base de datos
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import CierreMensual, Printer

def main():
    print("=" * 80)
    print("IMPRESORAS EN BASE DE DATOS")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        impresoras = db.query(Printer).all()
        
        print(f"\nTotal impresoras: {len(impresoras)}\n")
        
        for printer in impresoras:
            print(f"🖨️  ID: {printer.id}")
            print(f"   Hostname: {printer.hostname}")
            print(f"   Serial: {printer.serial_number}")
            print(f"   IP: {printer.ip_address}")
            print(f"   Ubicación: {printer.location if hasattr(printer, 'location') else 'N/A'}")
            
            # Contar cierres
            cierres = db.query(CierreMensual).filter(
                CierreMensual.printer_id == printer.id
            ).all()
            
            print(f"   Cierres: {len(cierres)}")
            
            if cierres:
                meses = ['', 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
                         'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
                
                for cierre in sorted(cierres, key=lambda c: (c.anio, c.mes)):
                    mes_nombre = meses[cierre.mes]
                    print(f"     • {mes_nombre} {cierre.anio}: {len(cierre.usuarios)} usuarios, {cierre.total_paginas:,} páginas")
            
            print()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
