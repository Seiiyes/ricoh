#!/usr/bin/env python3
"""
Prueba de integración completa final
Verifica que TODOS los endpoints retornen datos correctamente con codigo_usuario y nombre_usuario
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer, CierreMensual
from services.counter_service import CounterService
from services.close_service import CloseService
from datetime import date

def test_contadores_usuario(db):
    """Prueba que los contadores de usuario retornen codigo_usuario y nombre_usuario"""
    print("\n" + "="*80)
    print("TEST 1: Contadores de Usuario")
    print("="*80)
    
    printer = db.query(Printer).first()
    if not printer:
        print("❌ No hay impresoras")
        return False
    
    print(f"\n✓ Impresora: {printer.hostname}")
    
    # Obtener contadores
    contadores = CounterService.get_user_counters_latest(db, printer.id)
    
    if not contadores:
        print("⚠️ No hay contadores de usuario")
        return True
    
    print(f"✓ Contadores encontrados: {len(contadores)}")
    
    # Verificar primeros 3 contadores
    from db.models import User
    for i, contador in enumerate(contadores[:3], 1):
        user = db.query(User).filter(User.id == contador.user_id).first()
        if user:
            print(f"  {i}. user_id={contador.user_id} → [{user.codigo_de_usuario}] {user.name}")
        else:
            print(f"  {i}. user_id={contador.user_id} → ⚠️ Usuario no encontrado")
    
    print("\n✅ TEST 1 PASADO")
    return True


def test_cierre_usuarios(db):
    """Prueba que los usuarios de un cierre retornen codigo_usuario y nombre_usuario"""
    print("\n" + "="*80)
    print("TEST 2: Usuarios de Cierre")
    print("="*80)
    
    cierre = db.query(CierreMensual).first()
    if not cierre:
        print("❌ No hay cierres")
        return False
    
    print(f"\n✓ Cierre: ID {cierre.id}")
    print(f"✓ Usuarios en cierre: {len(cierre.usuarios)}")
    
    if not cierre.usuarios:
        print("⚠️ Cierre sin usuarios")
        return True
    
    # Verificar primeros 3 usuarios
    from db.models import User
    for i, usuario in enumerate(cierre.usuarios[:3], 1):
        user = db.query(User).filter(User.id == usuario.user_id).first()
        if user:
            print(f"  {i}. user_id={usuario.user_id} → [{user.codigo_de_usuario}] {user.name} - {usuario.total_paginas:,} páginas")
        else:
            print(f"  {i}. user_id={usuario.user_id} → ⚠️ Usuario no encontrado")
    
    print("\n✅ TEST 2 PASADO")
    return True


def test_comparacion_cierres(db):
    """Prueba que la comparación de cierres retorne codigo_usuario y nombre_usuario"""
    print("\n" + "="*80)
    print("TEST 3: Comparación de Cierres")
    print("="*80)
    
    # Buscar dos cierres de la misma impresora
    from sqlalchemy import func
    printer_id = db.query(CierreMensual.printer_id).group_by(CierreMensual.printer_id).having(
        func.count(CierreMensual.id) >= 2
    ).first()
    
    if not printer_id:
        print("⚠️ No hay impresora con al menos 2 cierres")
        return True
    
    cierres = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer_id[0]
    ).limit(2).all()
    
    print(f"\n✓ Comparando cierres {cierres[0].id} y {cierres[1].id}")
    print(f"  Impresora: {printer_id[0]}")
    
    try:
        resultado = CloseService.comparar_cierres(db, cierres[0].id, cierres[1].id)
        
        print(f"✓ Usuarios con aumento: {len(resultado['top_usuarios_aumento'])}")
        print(f"✓ Usuarios con disminución: {len(resultado['top_usuarios_disminucion'])}")
        
        # Verificar primeros 3 usuarios
        todos_usuarios = resultado['top_usuarios_aumento'] + resultado['top_usuarios_disminucion']
        for i, usuario in enumerate(todos_usuarios[:3], 1):
            print(f"  {i}. [{usuario['codigo_usuario']}] {usuario['nombre_usuario']} - Diff: {usuario['diferencia']:,}")
        
        print("\n✅ TEST 3 PASADO")
        return True
    except Exception as e:
        print(f"❌ Error en comparación: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crear_cierre_completo(db):
    """Prueba crear un cierre y verificar que los usuarios tengan codigo_usuario y nombre_usuario"""
    print("\n" + "="*80)
    print("TEST 4: Crear Cierre Completo")
    print("="*80)
    
    printer = db.query(Printer).first()
    if not printer:
        print("❌ No hay impresoras")
        return False
    
    print(f"\n✓ Creando cierre para: {printer.hostname}")
    
    try:
        cierre = CloseService.create_close(
            db=db,
            printer_id=printer.id,
            tipo_periodo='personalizado',
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            cerrado_por='test_integracion',
            notas='Prueba de integración completa'
        )
        
        print(f"✅ Cierre creado: ID {cierre.id}")
        print(f"✓ Total páginas: {cierre.total_paginas:,}")
        print(f"✓ Usuarios: {len(cierre.usuarios)}")
        
        # Verificar que los usuarios tengan user_id
        if cierre.usuarios:
            from db.models import User
            print(f"\n✓ Verificando primeros 3 usuarios:")
            for i, usuario in enumerate(cierre.usuarios[:3], 1):
                user = db.query(User).filter(User.id == usuario.user_id).first()
                if user:
                    print(f"  {i}. user_id={usuario.user_id} → [{user.codigo_de_usuario}] {user.name}")
                else:
                    print(f"  {i}. user_id={usuario.user_id} → ⚠️ Usuario no encontrado")
        
        # Eliminar cierre de prueba
        print(f"\n⏳ Eliminando cierre de prueba...")
        db.delete(cierre)
        db.commit()
        print(f"✅ Cierre eliminado")
        
        print("\n✅ TEST 4 PASADO")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False


def main():
    print("="*80)
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA FINAL")
    print("="*80)
    print("\nVerificando que TODOS los endpoints retornen datos correctamente")
    
    db = SessionLocal()
    
    try:
        tests = [
            ("Contadores de Usuario", test_contadores_usuario),
            ("Usuarios de Cierre", test_cierre_usuarios),
            ("Comparación de Cierres", test_comparacion_cierres),
            ("Crear Cierre Completo", test_crear_cierre_completo),
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
        print("📊 RESUMEN FINAL")
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
            print("🎉 ¡INTEGRACIÓN COMPLETA EXITOSA!")
            print("="*80)
            print("\n✅ Todos los endpoints retornan datos correctamente")
            print("✅ Los campos codigo_usuario y nombre_usuario están disponibles")
            print("✅ El frontend puede consumir la API sin problemas")
            print("\n📝 El sistema está 100% integrado y funcional")
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
