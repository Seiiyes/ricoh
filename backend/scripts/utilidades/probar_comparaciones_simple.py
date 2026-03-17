"""
Probar que la comparación funcione correctamente para TODAS las impresoras
Versión simplificada sin importar servicios
"""
import sys
sys.path.append('.')

from db.database import SessionLocal
from db.models import CierreMensual, Printer

def main():
    db = SessionLocal()
    
    try:
        # Obtener todas las impresoras
        printers = db.query(Printer).all()
        
        print("\n" + "="*80)
        print("VERIFICACIÓN DE DATOS PARA COMPARACIONES")
        print("="*80)
        
        problemas = []
        
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
                problemas.append(f"{printer.hostname}: No hay suficientes cierres")
                continue
            
            cierre_base = cierres[0]
            cierre_comparado = cierres[1]
            
            print(f"\n  Cierres disponibles para comparación:")
            print(f"    Base: Cierre {cierre_base.id} ({cierre_base.fecha_inicio} → {cierre_base.fecha_fin})")
            print(f"          {len(cierre_base.usuarios)} usuarios, {cierre_base.total_paginas:,} páginas")
            print(f"    Comparado: Cierre {cierre_comparado.id} ({cierre_comparado.fecha_inicio} → {cierre_comparado.fecha_fin})")
            print(f"               {len(cierre_comparado.usuarios)} usuarios, {cierre_comparado.total_paginas:,} páginas")
            
            # Verificar que ambos cierres pertenezcan a la misma impresora
            if cierre_base.printer_id != cierre_comparado.printer_id:
                print(f"\n  ✗ ERROR: Los cierres pertenecen a impresoras diferentes!")
                print(f"    Base: printer_id={cierre_base.printer_id}")
                print(f"    Comparado: printer_id={cierre_comparado.printer_id}")
                problemas.append(f"{printer.hostname}: Cierres de impresoras diferentes")
                continue
            
            # Verificar orden cronológico
            if cierre_base.fecha_inicio > cierre_comparado.fecha_inicio:
                print(f"\n  ⚠️ ADVERTENCIA: El cierre base es más reciente que el comparado")
                print(f"    Esto causará números negativos incorrectos")
                problemas.append(f"{printer.hostname}: Orden cronológico incorrecto")
            
            # Calcular diferencia simple
            diferencia_total = cierre_comparado.total_paginas - cierre_base.total_paginas
            
            print(f"\n  Diferencia esperada:")
            print(f"    Total: {diferencia_total:,} páginas")
            
            if diferencia_total < 0:
                print(f"    ⚠️ Diferencia negativa - puede indicar reseteo de contador")
            else:
                print(f"    ✓ Diferencia positiva - crecimiento normal")
            
            # Verificar usuarios
            usuarios_base = {u.codigo_usuario: u for u in cierre_base.usuarios}
            usuarios_comparado = {u.codigo_usuario: u for u in cierre_comparado.usuarios}
            
            usuarios_nuevos = set(usuarios_comparado.keys()) - set(usuarios_base.keys())
            usuarios_desaparecidos = set(usuarios_base.keys()) - set(usuarios_comparado.keys())
            
            print(f"\n  Análisis de usuarios:")
            print(f"    En base: {len(usuarios_base)}")
            print(f"    En comparado: {len(usuarios_comparado)}")
            print(f"    Nuevos en comparado: {len(usuarios_nuevos)}")
            print(f"    Desaparecidos: {len(usuarios_desaparecidos)}")
            
            if len(usuarios_nuevos) > 0:
                print(f"\n    Primeros 5 usuarios nuevos:")
                for codigo in list(usuarios_nuevos)[:5]:
                    u = usuarios_comparado[codigo]
                    print(f"      [{codigo}] {u.nombre_usuario} - {u.total_paginas:,} páginas")
            
            print(f"\n  ✓ Datos correctos para comparación")
        
        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        
        print(f"\nTotal de impresoras: {len(printers)}")
        print(f"Impresoras con problemas: {len(problemas)}")
        
        if problemas:
            print(f"\nProblemas encontrados:")
            for p in problemas:
                print(f"  - {p}")
        else:
            print(f"\n✓✓✓ TODAS LAS IMPRESORAS ESTÁN LISTAS PARA COMPARACIÓN ✓✓✓")
        
    finally:
        db.close()

if __name__ == '__main__':
    main()
