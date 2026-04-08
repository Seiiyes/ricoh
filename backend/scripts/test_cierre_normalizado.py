#!/usr/bin/env python3
"""
Script de prueba para verificar que los cierres usan user_id correctamente
"""
import sys
import os
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer, CierreMensual, CierreMensualUsuario, User
from services.close_service import CloseService


def main():
    """Prueba la creación de un cierre con normalización"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("PRUEBA DE NORMALIZACIÓN DE CIERRES")
        print("=" * 80)
        
        # 1. Obtener una impresora con contadores
        printer = db.query(Printer).filter(
            Printer.tiene_contador_usuario == True
        ).first()
        
        if not printer:
            print("❌ No hay impresoras con contadores de usuario")
            return
        
        print(f"\n📍 Impresora seleccionada:")
        print(f"   ID: {printer.id}")
        print(f"   Hostname: {printer.hostname}")
        print(f"   IP: {printer.ip_address}")
        
        # 2. Verificar que hay usuarios con user_id
        from db.models import ContadorUsuario
        usuarios_count = db.query(ContadorUsuario).filter(
            ContadorUsuario.printer_id == printer.id,
            ContadorUsuario.user_id.isnot(None)
        ).distinct(ContadorUsuario.user_id).count()
        
        print(f"\n👥 Usuarios con user_id en esta impresora: {usuarios_count}")
        
        if usuarios_count == 0:
            print("❌ No hay usuarios con user_id en esta impresora")
            return
        
        # 3. Obtener el último cierre para esta impresora
        ultimo_cierre = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer.id
        ).order_by(CierreMensual.fecha_fin.desc()).first()
        
        if ultimo_cierre:
            print(f"\n📅 Último cierre:")
            print(f"   Período: {ultimo_cierre.fecha_inicio} a {ultimo_cierre.fecha_fin}")
            print(f"   Tipo: {ultimo_cierre.tipo_periodo}")
            print(f"   Total páginas: {ultimo_cierre.total_paginas:,}")
            
            # Verificar cuántos usuarios tienen user_id en el último cierre
            usuarios_con_id = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == ultimo_cierre.id,
                CierreMensualUsuario.user_id.isnot(None)
            ).count()
            
            usuarios_sin_id = db.query(CierreMensualUsuario).filter(
                CierreMensualUsuario.cierre_mensual_id == ultimo_cierre.id,
                CierreMensualUsuario.user_id.is_(None)
            ).count()
            
            print(f"\n   Usuarios en cierre:")
            print(f"   ✅ Con user_id: {usuarios_con_id}")
            print(f"   ❌ Sin user_id: {usuarios_sin_id}")
            
            if usuarios_sin_id > 0:
                print(f"\n   ⚠️  ADVERTENCIA: Hay {usuarios_sin_id} usuarios sin user_id")
                print("   Esto indica que el cierre se creó antes de la normalización")
        else:
            print("\n📅 No hay cierres previos para esta impresora")
        
        # 4. Crear un cierre de prueba (diario de hoy)
        print("\n" + "=" * 80)
        print("CREANDO CIERRE DE PRUEBA")
        print("=" * 80)
        
        fecha_hoy = date.today()
        
        # Verificar si ya existe un cierre para hoy
        cierre_existente = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer.id,
            CierreMensual.tipo_periodo == 'diario',
            CierreMensual.fecha_inicio == fecha_hoy,
            CierreMensual.fecha_fin == fecha_hoy
        ).first()
        
        if cierre_existente:
            print(f"\n⚠️  Ya existe un cierre diario para hoy")
            print(f"   Usando cierre existente ID: {cierre_existente.id}")
            cierre_prueba = cierre_existente
        else:
            print(f"\n📝 Creando cierre diario para: {fecha_hoy}")
            
            try:
                cierre_prueba = CloseService.create_close(
                    db=db,
                    printer_id=printer.id,
                    fecha_inicio=fecha_hoy,
                    fecha_fin=fecha_hoy,
                    tipo_periodo='diario',
                    cerrado_por='test_script',
                    notas='Cierre de prueba para verificar normalización'
                )
                
                print(f"✅ Cierre creado exitosamente!")
                print(f"   ID: {cierre_prueba.id}")
                print(f"   Total páginas: {cierre_prueba.total_paginas:,}")
                
            except Exception as e:
                print(f"❌ Error al crear cierre: {e}")
                return
        
        # 5. Verificar que todos los usuarios tienen user_id
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DE NORMALIZACIÓN")
        print("=" * 80)
        
        usuarios_cierre = db.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.cierre_mensual_id == cierre_prueba.id
        ).all()
        
        print(f"\n📊 Total usuarios en cierre: {len(usuarios_cierre)}")
        
        usuarios_con_id = [u for u in usuarios_cierre if u.user_id is not None]
        usuarios_sin_id = [u for u in usuarios_cierre if u.user_id is None]
        
        print(f"   ✅ Con user_id: {len(usuarios_con_id)} ({len(usuarios_con_id)/len(usuarios_cierre)*100:.1f}%)")
        print(f"   ❌ Sin user_id: {len(usuarios_sin_id)} ({len(usuarios_sin_id)/len(usuarios_cierre)*100:.1f}%)")
        
        if len(usuarios_sin_id) > 0:
            print(f"\n⚠️  PROBLEMA: Hay {len(usuarios_sin_id)} usuarios sin user_id")
            print("\nUsuarios sin user_id:")
            for u in usuarios_sin_id[:5]:  # Mostrar solo los primeros 5
                print(f"   - {u.codigo_usuario}: {u.nombre_usuario}")
            if len(usuarios_sin_id) > 5:
                print(f"   ... y {len(usuarios_sin_id) - 5} más")
        else:
            print("\n✅ ÉXITO: Todos los usuarios tienen user_id")
        
        # 6. Verificar que los user_id son válidos
        print("\n" + "=" * 80)
        print("VERIFICACIÓN DE INTEGRIDAD")
        print("=" * 80)
        
        user_ids_validos = 0
        user_ids_invalidos = 0
        
        for usuario in usuarios_con_id[:10]:  # Verificar solo los primeros 10
            user = db.query(User).filter(User.id == usuario.user_id).first()
            if user:
                user_ids_validos += 1
            else:
                user_ids_invalidos += 1
                print(f"   ❌ user_id {usuario.user_id} no existe en tabla users")
        
        print(f"\n📊 Verificación de integridad (muestra de 10):")
        print(f"   ✅ user_id válidos: {user_ids_validos}")
        print(f"   ❌ user_id inválidos: {user_ids_invalidos}")
        
        if user_ids_invalidos == 0:
            print("\n✅ ÉXITO: Todos los user_id son válidos")
        
        # 7. Mostrar algunos ejemplos
        print("\n" + "=" * 80)
        print("EJEMPLOS DE USUARIOS EN CIERRE")
        print("=" * 80)
        
        for usuario in usuarios_con_id[:5]:
            user = db.query(User).filter(User.id == usuario.user_id).first()
            print(f"\n👤 Usuario:")
            print(f"   user_id: {usuario.user_id}")
            if user:
                print(f"   ✅ Existe en tabla users:")
                print(f"      Código: {user.codigo_de_usuario}")
                print(f"      Nombre: {user.name}")
                print(f"      SMB path: {user.smb_path}")
            print(f"   consumo_total: {usuario.consumo_total:,} páginas")
        
        print("\n" + "=" * 80)
        print("PRUEBA COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
