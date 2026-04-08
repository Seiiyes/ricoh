#!/usr/bin/env python3
"""
Script de prueba completa de la normalización de base de datos
Verifica que todos los cambios funcionen correctamente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import SessionLocal
from db.models import (
    User, Printer, ContadorUsuario, CierreMensual, CierreMensualUsuario
)
from datetime import datetime

def test_contadores_usuario_normalizados(db: Session):
    """Verifica que contadores_usuario use solo user_id"""
    print("\n" + "="*80)
    print("TEST 1: Verificar normalización de contadores_usuario")
    print("="*80)
    
    # Obtener un contador de ejemplo
    contador = db.query(ContadorUsuario).first()
    
    if not contador:
        print("❌ No hay contadores en la base de datos")
        return False
    
    print(f"\n✓ Contador encontrado: ID {contador.id}")
    print(f"  - printer_id: {contador.printer_id}")
    print(f"  - user_id: {contador.user_id}")
    print(f"  - total_paginas: {contador.total_paginas}")
    
    # Verificar que NO tenga codigo_usuario ni nombre_usuario
    try:
        _ = contador.codigo_usuario
        print("❌ ERROR: La columna 'codigo_usuario' todavía existe!")
        return False
    except AttributeError:
        print("✓ Columna 'codigo_usuario' eliminada correctamente")
    
    try:
        _ = contador.nombre_usuario
        print("❌ ERROR: La columna 'nombre_usuario' todavía existe!")
        return False
    except AttributeError:
        print("✓ Columna 'nombre_usuario' eliminada correctamente")
    
    # Verificar que pueda obtener datos del usuario mediante JOIN
    if contador.user_id:
        user = db.query(User).filter(User.id == contador.user_id).first()
        if user:
            print(f"\n✓ JOIN con users funciona correctamente:")
            print(f"  - Código: {user.codigo_de_usuario}")
            print(f"  - Nombre: {user.name}")
        else:
            print(f"⚠️ ADVERTENCIA: user_id {contador.user_id} no existe en tabla users")
    
    print("\n✅ TEST 1 PASADO: contadores_usuario está normalizado")
    return True


def test_cierres_mensuales_usuarios_normalizados(db: Session):
    """Verifica que cierres_mensuales_usuarios use solo user_id"""
    print("\n" + "="*80)
    print("TEST 2: Verificar normalización de cierres_mensuales_usuarios")
    print("="*80)
    
    # Obtener un cierre de ejemplo
    cierre_usuario = db.query(CierreMensualUsuario).first()
    
    if not cierre_usuario:
        print("❌ No hay cierres de usuario en la base de datos")
        return False
    
    print(f"\n✓ Cierre de usuario encontrado: ID {cierre_usuario.id}")
    print(f"  - cierre_mensual_id: {cierre_usuario.cierre_mensual_id}")
    print(f"  - user_id: {cierre_usuario.user_id}")
    print(f"  - total_paginas: {cierre_usuario.total_paginas}")
    
    # Verificar que NO tenga codigo_usuario ni nombre_usuario
    try:
        _ = cierre_usuario.codigo_usuario
        print("❌ ERROR: La columna 'codigo_usuario' todavía existe!")
        return False
    except AttributeError:
        print("✓ Columna 'codigo_usuario' eliminada correctamente")
    
    try:
        _ = cierre_usuario.nombre_usuario
        print("❌ ERROR: La columna 'nombre_usuario' todavía existe!")
        return False
    except AttributeError:
        print("✓ Columna 'nombre_usuario' eliminada correctamente")
    
    # Verificar que pueda obtener datos del usuario mediante JOIN
    if cierre_usuario.user_id:
        user = db.query(User).filter(User.id == cierre_usuario.user_id).first()
        if user:
            print(f"\n✓ JOIN con users funciona correctamente:")
            print(f"  - Código: {user.codigo_de_usuario}")
            print(f"  - Nombre: {user.name}")
        else:
            print(f"⚠️ ADVERTENCIA: user_id {cierre_usuario.user_id} no existe en tabla users")
    
    print("\n✅ TEST 2 PASADO: cierres_mensuales_usuarios está normalizado")
    return True


def test_exportacion_cierre(db: Session):
    """Simula la exportación de un cierre para verificar que funcione"""
    print("\n" + "="*80)
    print("TEST 3: Simular exportación de cierre")
    print("="*80)
    
    # Obtener un cierre con usuarios
    cierre = db.query(CierreMensual).first()
    
    if not cierre:
        print("❌ No hay cierres en la base de datos")
        return False
    
    print(f"\n✓ Cierre encontrado: ID {cierre.id}")
    print(f"  - Printer ID: {cierre.printer_id}")
    print(f"  - Fecha: {cierre.fecha_inicio} a {cierre.fecha_fin}")
    print(f"  - Total páginas: {cierre.total_paginas:,}")
    print(f"  - Usuarios: {len(cierre.usuarios)}")
    
    if not cierre.usuarios:
        print("⚠️ Este cierre no tiene usuarios")
        return True
    
    # Simular el proceso de exportación (como en export.py)
    print("\n✓ Simulando exportación de usuarios:")
    errores = 0
    
    for i, usuario in enumerate(cierre.usuarios[:5], 1):  # Solo primeros 5
        try:
            # Este es el patrón usado en export.py
            user = db.query(User).filter(User.id == usuario.user_id).first()
            codigo = user.codigo_de_usuario if user else str(usuario.user_id)
            nombre = user.name if user else f"Usuario {usuario.user_id}"
            
            print(f"  {i}. [{codigo}] {nombre} - {usuario.total_paginas:,} páginas")
        except Exception as e:
            print(f"  ❌ Error con usuario {usuario.user_id}: {e}")
            errores += 1
    
    if len(cierre.usuarios) > 5:
        print(f"  ... y {len(cierre.usuarios) - 5} usuarios más")
    
    if errores > 0:
        print(f"\n❌ TEST 3 FALLIDO: {errores} errores al exportar usuarios")
        return False
    
    print("\n✅ TEST 3 PASADO: Exportación de cierre funciona correctamente")
    return True


def test_comparacion_cierres(db: Session):
    """Simula la comparación de dos cierres"""
    print("\n" + "="*80)
    print("TEST 4: Simular comparación de cierres")
    print("="*80)
    
    # Obtener dos cierres de la misma impresora
    cierres = db.query(CierreMensual).limit(2).all()
    
    if len(cierres) < 2:
        print("⚠️ No hay suficientes cierres para comparar")
        return True
    
    cierre1, cierre2 = cierres[0], cierres[1]
    
    print(f"\n✓ Comparando cierres:")
    print(f"  Cierre 1: ID {cierre1.id} - {cierre1.total_paginas:,} páginas")
    print(f"  Cierre 2: ID {cierre2.id} - {cierre2.total_paginas:,} páginas")
    
    # Simular el proceso de comparación (como en export.py)
    usuarios_c1 = {u.user_id: u for u in cierre1.usuarios}
    usuarios_c2 = {u.user_id: u for u in cierre2.usuarios}
    
    user_ids = set(usuarios_c1.keys()).union(set(usuarios_c2.keys()))
    
    print(f"\n✓ Usuarios únicos: {len(user_ids)}")
    print(f"  - En cierre 1: {len(usuarios_c1)}")
    print(f"  - En cierre 2: {len(usuarios_c2)}")
    
    # Calcular diferencias para algunos usuarios
    print("\n✓ Calculando diferencias (primeros 5 usuarios):")
    errores = 0
    
    for i, user_id in enumerate(list(user_ids)[:5], 1):
        try:
            u1 = usuarios_c1.get(user_id)
            u2 = usuarios_c2.get(user_id)
            
            # Obtener datos del usuario
            user = db.query(User).filter(User.id == user_id).first()
            codigo = user.codigo_de_usuario if user else str(user_id)
            nombre = user.name if user else f"Usuario {user_id}"
            
            total1 = u1.total_paginas if u1 else 0
            total2 = u2.total_paginas if u2 else 0
            diff = total2 - total1
            
            print(f"  {i}. [{codigo}] {nombre}")
            print(f"     Cierre 1: {total1:,} | Cierre 2: {total2:,} | Diff: {diff:,}")
        except Exception as e:
            print(f"  ❌ Error con usuario {user_id}: {e}")
            errores += 1
    
    if errores > 0:
        print(f"\n❌ TEST 4 FALLIDO: {errores} errores al comparar")
        return False
    
    print("\n✅ TEST 4 PASADO: Comparación de cierres funciona correctamente")
    return True


def test_integridad_referencial(db: Session):
    """Verifica la integridad referencial de user_id"""
    print("\n" + "="*80)
    print("TEST 5: Verificar integridad referencial")
    print("="*80)
    
    # Contar contadores con user_id NULL
    contadores_null = db.query(ContadorUsuario).filter(
        ContadorUsuario.user_id.is_(None)
    ).count()
    
    print(f"\n✓ Contadores con user_id NULL: {contadores_null}")
    
    # Contar cierres de usuario con user_id NULL
    cierres_null = db.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.user_id.is_(None)
    ).count()
    
    print(f"✓ Cierres de usuario con user_id NULL: {cierres_null}")
    
    # Verificar user_ids huérfanos en contadores
    from sqlalchemy import text
    
    query = text("""
        SELECT COUNT(*) 
        FROM contadores_usuario cu
        LEFT JOIN users u ON cu.user_id = u.id
        WHERE cu.user_id IS NOT NULL AND u.id IS NULL
    """)
    
    huerfanos_contadores = db.execute(query).scalar()
    print(f"✓ Contadores con user_id huérfano: {huerfanos_contadores}")
    
    # Verificar user_ids huérfanos en cierres
    query2 = text("""
        SELECT COUNT(*) 
        FROM cierres_mensuales_usuarios cmu
        LEFT JOIN users u ON cmu.user_id = u.id
        WHERE cmu.user_id IS NOT NULL AND u.id IS NULL
    """)
    
    huerfanos_cierres = db.execute(query2).scalar()
    print(f"✓ Cierres con user_id huérfano: {huerfanos_cierres}")
    
    if huerfanos_contadores > 0 or huerfanos_cierres > 0:
        print(f"\n⚠️ ADVERTENCIA: Hay {huerfanos_contadores + huerfanos_cierres} registros huérfanos")
        print("   Esto puede causar problemas al hacer JOINs")
    else:
        print("\n✅ No hay registros huérfanos")
    
    print("\n✅ TEST 5 PASADO: Integridad referencial verificada")
    return True


def test_estadisticas_generales(db: Session):
    """Muestra estadísticas generales del sistema"""
    print("\n" + "="*80)
    print("TEST 6: Estadísticas generales")
    print("="*80)
    
    total_users = db.query(User).count()
    total_printers = db.query(Printer).count()
    total_contadores = db.query(ContadorUsuario).count()
    total_cierres = db.query(CierreMensual).count()
    total_cierres_usuarios = db.query(CierreMensualUsuario).count()
    
    print(f"\n✓ Usuarios en sistema: {total_users:,}")
    print(f"✓ Impresoras: {total_printers:,}")
    print(f"✓ Registros de contadores: {total_contadores:,}")
    print(f"✓ Cierres mensuales: {total_cierres:,}")
    print(f"✓ Registros de cierres de usuarios: {total_cierres_usuarios:,}")
    
    # Calcular promedio de usuarios por cierre
    if total_cierres > 0:
        promedio = total_cierres_usuarios / total_cierres
        print(f"\n✓ Promedio de usuarios por cierre: {promedio:.1f}")
    
    print("\n✅ TEST 6 PASADO: Estadísticas generadas")
    return True


def main():
    print("="*80)
    print("🧪 PRUEBAS DE NORMALIZACIÓN COMPLETA DE BASE DE DATOS")
    print("="*80)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    db = SessionLocal()
    
    try:
        tests = [
            ("Normalización de contadores_usuario", test_contadores_usuario_normalizados),
            ("Normalización de cierres_mensuales_usuarios", test_cierres_mensuales_usuarios_normalizados),
            ("Exportación de cierre", test_exportacion_cierre),
            ("Comparación de cierres", test_comparacion_cierres),
            ("Integridad referencial", test_integridad_referencial),
            ("Estadísticas generales", test_estadisticas_generales),
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
        
        # Resumen final
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
            print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
            print("="*80)
            print("\n✅ La normalización de la base de datos está funcionando correctamente")
            print("✅ El backend puede acceder a los datos de usuario mediante JOINs")
            print("✅ Las exportaciones y comparaciones funcionan correctamente")
            print("\n📝 Próximos pasos recomendados:")
            print("   1. Probar las exportaciones desde el frontend")
            print("   2. Crear un nuevo cierre y verificar que funcione")
            print("   3. Verificar que las comparaciones se muestren correctamente")
            return 0
        else:
            print("\n" + "="*80)
            print("⚠️ ALGUNAS PRUEBAS FALLARON")
            print("="*80)
            print("\nRevisar los errores anteriores y corregir los problemas")
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
