#!/usr/bin/env python3
"""
Script para ver diferencias de consumo entre dos fechas
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.database import get_db
from db.models import Printer, ContadorImpresora, ContadorUsuario
from sqlalchemy import func


def ver_diferencia_diaria():
    """Muestra diferencias de consumo entre dos lecturas"""
    
    print("=" * 80)
    print("📊 DIFERENCIA DE CONSUMO ENTRE DOS LECTURAS")
    print("=" * 80)
    print()
    
    db = next(get_db())
    
    try:
        # 1. Listar impresoras
        print("📋 Impresoras disponibles:")
        print("-" * 80)
        printers = db.query(Printer).all()
        
        if not printers:
            print("❌ No hay impresoras registradas")
            return
        
        for p in printers:
            print(f"  ID: {p.id:3d} | IP: {p.ip_address:15s} | Hostname: {p.hostname or 'N/A'}")
        
        print()
        printer_id = int(input("Ingrese ID de impresora: "))
        
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if not printer:
            print(f"❌ Impresora {printer_id} no encontrada")
            return
        
        print(f"✅ Impresora seleccionada: {printer.hostname or printer.ip_address}")
        print()
        
        # 2. Obtener últimas lecturas
        print("📅 Últimas 10 lecturas de contadores totales:")
        print("-" * 80)
        
        lecturas = db.query(ContadorImpresora).filter(
            ContadorImpresora.printer_id == printer_id
        ).order_by(ContadorImpresora.fecha_lectura.desc()).limit(10).all()
        
        if not lecturas:
            print("❌ No hay lecturas de contadores")
            return
        
        for i, l in enumerate(lecturas, 1):
            fecha_str = l.fecha_lectura.strftime('%Y-%m-%d %H:%M:%S')
            print(f"  {i:2d}. {fecha_str} | Total: {l.total:>10,} páginas")
        
        print()
        
        # 3. Seleccionar dos lecturas
        print("Seleccione dos lecturas para comparar:")
        lectura1_idx = int(input(f"Primera lectura (1-{len(lecturas)}) [más reciente]: ") or "1") - 1
        lectura2_idx = int(input(f"Segunda lectura (1-{len(lecturas)}) [más antigua]: ") or "2") - 1
        
        if lectura1_idx < 0 or lectura1_idx >= len(lecturas):
            print("❌ Índice inválido para primera lectura")
            return
        
        if lectura2_idx < 0 or lectura2_idx >= len(lecturas):
            print("❌ Índice inválido para segunda lectura")
            return
        
        lectura_nueva = lecturas[lectura1_idx]
        lectura_antigua = lecturas[lectura2_idx]
        
        # Asegurar que lectura_nueva sea más reciente
        if lectura_nueva.fecha_lectura < lectura_antigua.fecha_lectura:
            lectura_nueva, lectura_antigua = lectura_antigua, lectura_nueva
        
        print()
        print("=" * 80)
        print("📊 COMPARACIÓN DE LECTURAS")
        print("=" * 80)
        print()
        
        # 4. Mostrar diferencias de totales
        print("📈 CONTADORES TOTALES:")
        print("-" * 80)
        print(f"Lectura antigua: {lectura_antigua.fecha_lectura.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Lectura nueva:   {lectura_nueva.fecha_lectura.strftime('%Y-%m-%d %H:%M:%S')}")
        
        tiempo_transcurrido = lectura_nueva.fecha_lectura - lectura_antigua.fecha_lectura
        dias = tiempo_transcurrido.days
        horas = tiempo_transcurrido.seconds // 3600
        print(f"Tiempo:          {dias} días, {horas} horas")
        print()
        
        diff_total = lectura_nueva.total - lectura_antigua.total
        diff_copiadora = max(lectura_nueva.copiadora_bn, lectura_nueva.copiadora_color) - \
                        max(lectura_antigua.copiadora_bn, lectura_antigua.copiadora_color)
        diff_impresora = max(lectura_nueva.impresora_bn, lectura_nueva.impresora_color) - \
                        max(lectura_antigua.impresora_bn, lectura_antigua.impresora_color)
        diff_escaner = max(lectura_nueva.envio_escaner_bn, lectura_nueva.envio_escaner_color) - \
                      max(lectura_antigua.envio_escaner_bn, lectura_antigua.envio_escaner_color)
        
        print(f"{'Función':<20} {'Antigua':>15} {'Nueva':>15} {'Diferencia':>15}")
        print("-" * 80)
        print(f"{'Total páginas':<20} {lectura_antigua.total:>15,} {lectura_nueva.total:>15,} {diff_total:>15,}")
        print(f"{'Copiadora':<20} {max(lectura_antigua.copiadora_bn, lectura_antigua.copiadora_color):>15,} "
              f"{max(lectura_nueva.copiadora_bn, lectura_nueva.copiadora_color):>15,} {diff_copiadora:>15,}")
        print(f"{'Impresora':<20} {max(lectura_antigua.impresora_bn, lectura_antigua.impresora_color):>15,} "
              f"{max(lectura_nueva.impresora_bn, lectura_nueva.impresora_color):>15,} {diff_impresora:>15,}")
        print(f"{'Escáner':<20} {max(lectura_antigua.envio_escaner_bn, lectura_antigua.envio_escaner_color):>15,} "
              f"{max(lectura_nueva.envio_escaner_bn, lectura_nueva.envio_escaner_color):>15,} {diff_escaner:>15,}")
        print()
        
        # 5. Obtener usuarios con mayor consumo
        print("👥 TOP 10 USUARIOS CON MAYOR CONSUMO:")
        print("-" * 80)
        
        # Obtener contadores de usuarios más cercanos a las fechas seleccionadas
        # Buscar lecturas de usuarios en un rango de ±5 minutos
        from datetime import timedelta
        
        margen = timedelta(minutes=5)
        
        usuarios_nuevos = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer_id,
            ContadorUsuario.fecha_lectura >= lectura_nueva.fecha_lectura - margen,
            ContadorUsuario.fecha_lectura <= lectura_nueva.fecha_lectura + margen
        ).all()
        
        usuarios_antiguos = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer_id,
            ContadorUsuario.fecha_lectura >= lectura_antigua.fecha_lectura - margen,
            ContadorUsuario.fecha_lectura <= lectura_antigua.fecha_lectura + margen
        ).all()
        
        print(f"Debug: Encontrados {len(usuarios_nuevos)} usuarios en lectura nueva")
        print(f"Debug: Encontrados {len(usuarios_antiguos)} usuarios en lectura antigua")
        print()
        
        # Crear diccionario de usuarios antiguos
        usuarios_antiguos_dict = {u.codigo_usuario: u for u in usuarios_antiguos}
        
        # Calcular diferencias por usuario
        diferencias_usuarios = []
        
        for u_nuevo in usuarios_nuevos:
            u_antiguo = usuarios_antiguos_dict.get(u_nuevo.codigo_usuario)
            
            if u_antiguo:
                diff = u_nuevo.total_paginas - u_antiguo.total_paginas
                if diff > 0:  # Solo usuarios con consumo
                    diferencias_usuarios.append({
                        'codigo': u_nuevo.codigo_usuario,
                        'nombre': u_nuevo.nombre_usuario,
                        'antiguo': u_antiguo.total_paginas,
                        'nuevo': u_nuevo.total_paginas,
                        'diferencia': diff
                    })
        
        # Ordenar por diferencia descendente
        diferencias_usuarios.sort(key=lambda x: x['diferencia'], reverse=True)
        
        if diferencias_usuarios:
            print(f"{'Código':<10} {'Nombre':<30} {'Antiguo':>12} {'Nuevo':>12} {'Consumo':>12}")
            print("-" * 80)
            
            for u in diferencias_usuarios[:10]:
                print(f"{u['codigo']:<10} {u['nombre']:<30} {u['antiguo']:>12,} "
                      f"{u['nuevo']:>12,} {u['diferencia']:>12,}")
            
            print()
            print(f"Total usuarios con consumo: {len(diferencias_usuarios)}")
            suma_consumos = sum(u['diferencia'] for u in diferencias_usuarios)
            print(f"Suma de consumos usuarios: {suma_consumos:,}")
            print(f"Total impresora: {diff_total:,}")
            diferencia_validacion = abs(suma_consumos - diff_total)
            porcentaje = (diferencia_validacion / diff_total * 100) if diff_total > 0 else 0
            print(f"Diferencia: {diferencia_validacion:,} ({porcentaje:.2f}%)")
        else:
            print("(No hay usuarios con consumo en este período)")
        
        print()
        print("=" * 80)
        print("✅ Comparación completada")
        print("=" * 80)
        
    except ValueError as e:
        print()
        print("=" * 80)
        print("❌ ERROR")
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
    ver_diferencia_diaria()
