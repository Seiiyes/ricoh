#!/usr/bin/env python3
"""
Script para consolidar códigos de usuario duplicados
Cambia códigos sin cero al inicio para que coincidan con el formato correcto
Ejemplo: 931 → 0931, 455 → 0455
"""
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.database import get_db, engine
from db.models import ContadorUsuario, CierreMensualUsuario
from datetime import datetime

def find_duplicates(session):
    """Encuentra usuarios con códigos duplicados (con y sin cero)"""
    print("\n" + "="*80)
    print("BUSCANDO CÓDIGOS DUPLICADOS")
    print("="*80)
    
    # Buscar códigos que existen en ambas formas (con y sin cero)
    query = text("""
        WITH codigos_normalizados AS (
            SELECT DISTINCT
                codigo_usuario,
                LPAD(LTRIM(codigo_usuario, '0'), 4, '0') as codigo_con_cero,
                LTRIM(codigo_usuario, '0') as codigo_sin_cero
            FROM contadores_usuario
            WHERE codigo_usuario ~ '^[0-9]+$'  -- Solo códigos numéricos
        )
        SELECT 
            c1.codigo_usuario as codigo_con_cero,
            c2.codigo_usuario as codigo_sin_cero,
            (SELECT nombre_usuario FROM contadores_usuario WHERE codigo_usuario = c1.codigo_usuario LIMIT 1) as nombre,
            (SELECT COUNT(*) FROM contadores_usuario WHERE codigo_usuario = c1.codigo_usuario) as count_con_cero,
            (SELECT COUNT(*) FROM contadores_usuario WHERE codigo_usuario = c2.codigo_usuario) as count_sin_cero
        FROM codigos_normalizados c1
        JOIN codigos_normalizados c2 
            ON c1.codigo_con_cero = c2.codigo_con_cero 
            AND c1.codigo_usuario != c2.codigo_usuario
            AND LENGTH(c1.codigo_usuario) = 4
            AND LENGTH(c2.codigo_usuario) < 4
        ORDER BY nombre
    """)
    
    result = session.execute(query)
    duplicates = result.fetchall()
    
    if not duplicates:
        print("\n✅ No se encontraron códigos duplicados")
        return []
    
    print(f"\n⚠️  Se encontraron {len(duplicates)} usuarios con códigos duplicados:")
    print("\n{:<15} {:<15} {:<25} {:<10} {:<10}".format(
        "Con cero", "Sin cero", "Nombre", "Registros", "Registros"
    ))
    print("{:<15} {:<15} {:<25} {:<10} {:<10}".format(
        "", "", "", "(con 0)", "(sin 0)"
    ))
    print("-" * 85)
    
    for dup in duplicates:
        print("{:<15} {:<15} {:<25} {:<10} {:<10}".format(
            dup[0], dup[1], dup[2][:24], dup[3], dup[4]
        ))
    
    return duplicates

def consolidate_contadores_usuario(session, duplicates):
    """Consolida códigos en tabla contadores_usuario"""
    print("\n" + "="*80)
    print("CONSOLIDANDO TABLA: contadores_usuario")
    print("="*80)
    
    if not duplicates:
        print("✅ No hay duplicados para consolidar")
        return 0
    
    print(f"\n📝 Se cambiarán los códigos sin cero al formato de 4 dígitos:")
    for dup in duplicates:
        print(f"   '{dup[1]}' → '{dup[0]}' ({dup[2]})")
    
    print(f"\n⚠️  Total de registros a actualizar: {sum(d[4] for d in duplicates)}")
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return 0
    
    # Actualizar códigos
    updated = 0
    for dup in duplicates:
        codigo_correcto = dup[0]  # Con cero
        codigo_incorrecto = dup[1]  # Sin cero
        
        # Actualizar todos los registros con el código incorrecto
        contadores = session.query(ContadorUsuario).filter(
            ContadorUsuario.codigo_usuario == codigo_incorrecto
        ).all()
        
        for contador in contadores:
            contador.codigo_usuario = codigo_correcto
            updated += 1
    
    session.commit()
    print(f"\n✅ {updated} registros actualizados")
    
    return updated

def consolidate_cierre_mensual_usuario(session, duplicates):
    """Consolida códigos en tabla cierre_mensual_usuario"""
    print("\n" + "="*80)
    print("CONSOLIDANDO TABLA: cierre_mensual_usuario")
    print("="*80)
    
    if not duplicates:
        print("✅ No hay duplicados para consolidar")
        return 0
    
    # Buscar duplicados en cierres
    codigos_incorrectos = [dup[1] for dup in duplicates]
    
    detalles = session.query(CierreMensualUsuario).filter(
        CierreMensualUsuario.codigo_usuario.in_(codigos_incorrectos)
    ).all()
    
    if not detalles:
        print("✅ No se encontraron registros con códigos incorrectos")
        return 0
    
    print(f"\n📊 Registros encontrados: {len(detalles)}")
    print(f"\n⚠️  Se actualizarán {len(detalles)} registros")
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return 0
    
    # Crear mapa de códigos incorrectos → correctos
    codigo_map = {dup[1]: dup[0] for dup in duplicates}
    
    # Actualizar códigos
    updated = 0
    for detalle in detalles:
        if detalle.codigo_usuario in codigo_map:
            detalle.codigo_usuario = codigo_map[detalle.codigo_usuario]
            updated += 1
    
    session.commit()
    print(f"\n✅ {updated} registros actualizados")
    
    return updated

def verify_no_duplicates(session):
    """Verifica que no queden duplicados después de la consolidación"""
    print("\n" + "="*80)
    print("VERIFICANDO RESULTADO")
    print("="*80)
    
    # Buscar duplicados en contadores_usuario
    query = text("""
        SELECT 
            printer_id,
            codigo_usuario,
            nombre_usuario,
            fecha_lectura,
            COUNT(*) as count
        FROM contadores_usuario
        GROUP BY printer_id, codigo_usuario, nombre_usuario, fecha_lectura
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    
    result = session.execute(query)
    duplicates = result.fetchall()
    
    if duplicates:
        print(f"\n⚠️  Aún hay {len(duplicates)} grupos de duplicados:")
        for dup in duplicates:
            print(f"   - Printer {dup[0]}, Código '{dup[1]}', {dup[2]}: {dup[4]} registros")
        print("\n💡 Estos pueden ser registros legítimos del mismo usuario en diferentes fechas")
    else:
        print("\n✅ No se encontraron duplicados por código")
    
    return len(duplicates)

def main():
    print("="*80)
    print("🔧 SCRIPT DE CONSOLIDACIÓN DE CÓDIGOS DUPLICADOS")
    print("="*80)
    print("\nEste script consolidará códigos de usuario duplicados")
    print("Cambiará códigos sin cero al formato correcto de 4 dígitos")
    print("Ejemplo: '931' → '0931', '455' → '0455'")
    print("\n⚠️  IMPORTANTE: Asegúrate de tener un backup de la base de datos")
    
    # Crear sesión
    session = next(get_db())
    
    try:
        # Buscar duplicados
        duplicates = find_duplicates(session)
        
        if not duplicates:
            print("\n🎉 No hay duplicados para consolidar")
            return
        
        # Consolidar contadores_usuario
        updated_contadores = consolidate_contadores_usuario(session, duplicates)
        
        # Consolidar cierre_mensual_usuario
        updated_cierres = consolidate_cierre_mensual_usuario(session, duplicates)
        
        # Verificar resultado
        remaining = verify_no_duplicates(session)
        
        # Resumen
        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        print(f"\n✅ Usuarios con códigos duplicados encontrados: {len(duplicates)}")
        print(f"✅ Registros actualizados en contadores_usuario: {updated_contadores}")
        print(f"✅ Registros actualizados en cierre_mensual_usuario: {updated_cierres}")
        print(f"⚠️  Grupos de duplicados restantes: {remaining}")
        
        if remaining > 0:
            print("\n💡 Los duplicados restantes son probablemente del mismo usuario")
            print("   en diferentes fechas, lo cual es correcto")
        
        print("\n🎉 Consolidación completada")
        print("\n📝 PRÓXIMOS PASOS:")
        print("   1. Hacer una nueva lectura manual de la impresora 253")
        print("   2. Crear un nuevo cierre con los datos corregidos")
        print("   3. Verificar que no aparezcan usuarios duplicados")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
