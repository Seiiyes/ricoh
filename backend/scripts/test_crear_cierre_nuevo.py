#!/usr/bin/env python3
"""
Script para probar la creación de un nuevo cierre
Verifica que el proceso completo funcione con la base de datos normalizada
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import Printer, User
from services.close_service import CloseService
from datetime import date, datetime

def main():
    print("="*80)
    print("🧪 PRUEBA DE CREACIÓN DE CIERRE NUEVO")
    print("="*80)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = SessionLocal()
    
    try:
        # Obtener una impresora para probar
        printer = db.query(Printer).first()
        
        if not printer:
            print("❌ No hay impresoras en la base de datos")
            return 1
        
        print(f"\n✓ Impresora seleccionada:")
        print(f"  - ID: {printer.id}")
        print(f"  - Hostname: {printer.hostname}")
        print(f"  - IP: {printer.ip_address}")
        
        # Definir período de prueba (hoy)
        fecha_inicio = date.today()
        fecha_fin = date.today()
        
        print(f"\n✓ Período del cierre:")
        print(f"  - Inicio: {fecha_inicio}")
        print(f"  - Fin: {fecha_fin}")
        
        print("\n⏳ Creando cierre de prueba...")
        
        # Crear cierre usando CloseService
        cierre = CloseService.create_close(
            db=db,
            printer_id=printer.id,
            tipo_periodo='personalizado',
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            cerrado_por='test_script',
            notas='Cierre de prueba para verificar normalización'
        )
        
        print(f"\n✅ Cierre creado exitosamente!")
        print(f"  - ID: {cierre.id}")
        print(f"  - Total páginas: {cierre.total_paginas:,}")
        print(f"  - Usuarios: {len(cierre.usuarios)}")
        
        # Verificar que los usuarios tengan user_id
        print("\n✓ Verificando usuarios del cierre:")
        
        usuarios_sin_user_id = [u for u in cierre.usuarios if not u.user_id]
        
        if usuarios_sin_user_id:
            print(f"  ❌ {len(usuarios_sin_user_id)} usuarios sin user_id!")
            return 1
        
        print(f"  ✅ Todos los usuarios tienen user_id")
        
        # Verificar que NO tengan codigo_usuario ni nombre_usuario
        print("\n✓ Verificando que no existan columnas redundantes:")
        
        for usuario in cierre.usuarios[:3]:  # Verificar primeros 3
            try:
                _ = usuario.codigo_usuario
                print("  ❌ ERROR: La columna 'codigo_usuario' existe!")
                return 1
            except AttributeError:
                pass
            
            try:
                _ = usuario.nombre_usuario
                print("  ❌ ERROR: La columna 'nombre_usuario' existe!")
                return 1
            except AttributeError:
                pass
        
        print("  ✅ Columnas redundantes no existen")
        
        # Verificar que se puedan obtener datos de usuario mediante JOIN
        print("\n✓ Verificando acceso a datos de usuario (primeros 5):")
        
        for i, usuario in enumerate(cierre.usuarios[:5], 1):
            user = db.query(User).filter(User.id == usuario.user_id).first()
            if user:
                codigo = user.codigo_de_usuario
                nombre = user.name
                print(f"  {i}. [{codigo}] {nombre} - {usuario.total_paginas:,} páginas")
            else:
                print(f"  ⚠️ Usuario {usuario.user_id} no encontrado en tabla users")
        
        if len(cierre.usuarios) > 5:
            print(f"  ... y {len(cierre.usuarios) - 5} usuarios más")
        
        print("\n✅ Acceso a datos de usuario funciona correctamente")
        
        # Eliminar el cierre de prueba
        print("\n⏳ Eliminando cierre de prueba...")
        db.delete(cierre)
        db.commit()
        print("✅ Cierre de prueba eliminado")
        
        print("\n" + "="*80)
        print("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
        print("="*80)
        print("\n✅ La creación de cierres funciona correctamente")
        print("✅ Los usuarios se guardan con user_id (normalizado)")
        print("✅ No hay columnas redundantes")
        print("✅ El acceso a datos de usuario mediante JOIN funciona")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
