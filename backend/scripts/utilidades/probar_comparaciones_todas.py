"""
Probar que la comparación funcione correctamente para TODAS las impresoras
"""
import sys
sys.path.append('.')

from db.database import SessionLocal
from db.models import CierreMensual, Printer
from services.close_service import CloseService

def main():
    db = SessionLocal()
    
    try:
        # Obtener todas las impresoras
        printers = db.query(Printer).all()
        
        print("\n" + "="*80)
        print("PRUEBA DE COMPARACIONES PARA TODAS LAS IMPRESORAS")
        print("="*80)
        
        for printer in printers:
            print(f"\n{'='*80}")
            print(f"IMPRESORA: {printer.hostname} ({printer.serial_number})")
            print(f"ID: {printer.id} | IP: {printer.ip_address}")
            print(f"{'='*80}")
            
            # Obtener los dos primeros cierres (más antiguos)
            cierres = db.query(CierreMensual).filter(
                CierreMensual.printer_id == printer.id
            ).order_by(CierreMensual.fecha_inicio).limit(2).all()
            
            if len(cierres) < 2:
                print("  ⚠️ No hay suficientes cierres para comparar")
                continue
            
            cierre_base = cierres[0]
            cierre_comparado = cierres[1]
            
            print(f"\n  Comparando:")
            print(f"    Base: Cierre {cierre_base.id} ({cierre_base.fecha_inicio} → {cierre_base.fecha_fin})")
            print(f"          {len(cierre_base.usuarios)} usuarios, {cierre_base.total_paginas:,} páginas")
            print(f"    Comparado: Cierre {cierre_comparado.id} ({cierre_comparado.fecha_inicio} → {cierre_comparado.fecha_fin})")
            print(f"               {len(cierre_comparado.usuarios)} usuarios, {cierre_comparado.total_paginas:,} páginas")
            
            try:
                # Intentar hacer la comparación
                resultado = CloseService.comparar_cierres(db, cierre_base.id, cierre_comparado.id)
                
                print(f"\n  ✓ COMPARACIÓN EXITOSA")
                print(f"    Diferencia total: {resultado['diferencia_total']:,} páginas")
                print(f"    Días entre cierres: {resultado['dias_entre_cierres']}")
                print(f"    Usuarios activos: {resultado['total_usuarios_activos']}")
                print(f"    Promedio por usuario: {resultado['promedio_consumo_por_usuario']:.2f}")
                
                # Verificar que no haya números negativos incorrectos
                usuarios_negativos = [u for u in resultado['top_usuarios_disminucion'] if u['diferencia'] < 0]
                if usuarios_negativos:
                    print(f"\n    ⚠️ Usuarios con diferencias negativas: {len(usuarios_negativos)}")
                    # Mostrar algunos ejemplos
                    for u in usuarios_negativos[:3]:
                        print(f"      - [{u['codigo_usuario']}] {u['nombre_usuario']}: {u['diferencia']:,} páginas")
                        print(f"        Base: {u['consumo_cierre1']:,}, Comparado: {u['consumo_cierre2']:,}")
                
                # Verificar capacidades de la impresora
                if resultado['printer']:
                    print(f"\n    Capacidades detectadas:")
                    print(f"      Color: {resultado['printer']['has_color']}")
                    print(f"      Scanner: {resultado['printer']['has_scanner']}")
                    print(f"      Fax: {resultado['printer']['has_fax']}")
                
            except Exception as e:
                print(f"\n  ✗ ERROR EN COMPARACIÓN: {str(e)}")
        
        print("\n" + "="*80)
        print("RESUMEN DE PRUEBAS")
        print("="*80)
        
        exitosas = 0
        fallidas = 0
        
        for printer in printers:
            cierres = db.query(CierreMensual).filter(
                CierreMensual.printer_id == printer.id
            ).order_by(CierreMensual.fecha_inicio).limit(2).all()
            
            if len(cierres) < 2:
                continue
            
            try:
                CloseService.comparar_cierres(db, cierres[0].id, cierres[1].id)
                exitosas += 1
            except:
                fallidas += 1
        
        print(f"\nTotal de impresoras probadas: {len(printers)}")
        print(f"  ✓ Comparaciones exitosas: {exitosas}")
        print(f"  ✗ Comparaciones fallidas: {fallidas}")
        
        if exitosas == len(printers):
            print(f"\n✓✓✓ TODAS LAS COMPARACIONES FUNCIONAN CORRECTAMENTE ✓✓✓")
        elif fallidas > 0:
            print(f"\n⚠️ Hay {fallidas} impresora(s) con problemas en la comparación")
        
    finally:
        db.close()

if __name__ == '__main__':
    main()
