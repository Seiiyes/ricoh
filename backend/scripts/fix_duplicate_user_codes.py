#!/usr/bin/env python3
"""
Script para corregir códigos de usuario duplicados
Normaliza códigos eliminando ceros al inicio
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

def normalize_code(code: str) -> str:
    """Normaliza código de usuario eliminando ceros al inicio"""
    if not code:
        return '0'
    normalized = code.lstrip('0')
    return normalized if normalized else '0'

def fix_contadores_usuario(session):
    """Corrige códigos en tabla contadores_usuario"""
    print("\n" + "="*80)
    print("CORRIGIENDO TABLA: contadores_usuario")
    print("="*80)
    
    # Obtener todos los contadores
    contadores = session.query(ContadorUsuario).all()
    print(f"\n📊 Total de registros: {len(contadores)}")
    
    # Agrupar por código original para ver duplicados
    codes_map = {}
    for contador in contadores:
        original = contador.codigo_usuario
        normalized = normalize_code(original)
        
        if original != normalized:
            if original not in codes_map:
                codes_map[original] = []
            codes_map[original].append({
                'id': contador.id,
                'nombre': contador.nombre_usuario,
                'printer_id': contador.printer_id,
                'fecha': contador.fecha_lectura,
                'normalized': normalized
            })
    
    if not codes_map:
        print("✅ No se encontraron códigos para normalizar")
        return 0
    
    print(f"\n🔍 Códigos a normalizar: {len(codes_map)}")
    
    # Mostrar ejemplos
    print("\n📝 Ejemplos de normalización:")
    for i, (original, items) in enumerate(list(codes_map.items())[:5]):
        normalized = items[0]['normalized']
        print(f"   {i+1}. '{original}' → '{normalized}' ({len(items)} registros)")
    
    # Confirmar
    print(f"\n⚠️  Se actualizarán {sum(len(items) for items in codes_map.values())} registros")
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return 0
    
    # Actualizar códigos
    updated = 0
    for original, items in codes_map.items():
        normalized = items[0]['normalized']
        
        for item in items:
            contador = session.query(ContadorUsuario).get(item['id'])
            if contador:
                contador.codigo_usuario = normalized
                updated += 1
    
    session.commit()
    print(f"\n✅ {updated} registros actualizados")
    
    return updated

def fix_cierre_detalle(session):
    """Corrige códigos en tabla cierre_mensual_usuario"""
    print("\n" + "="*80)
    print("CORRIGIENDO TABLA: cierre_mensual_usuario")
    print("="*80)
    
    # Obtener todos los detalles
    detalles = session.query(CierreMensualUsuario).all()
    print(f"\n📊 Total de registros: {len(detalles)}")
    
    # Agrupar por código original
    codes_map = {}
    for detalle in detalles:
        original = detalle.codigo_usuario
        normalized = normalize_code(original)
        
        if original != normalized:
            if original not in codes_map:
                codes_map[original] = []
            codes_map[original].append({
                'id': detalle.id,
                'nombre': detalle.nombre_usuario,
                'cierre_id': detalle.cierre_id,
                'normalized': normalized
            })
    
    if not codes_map:
        print("✅ No se encontraron códigos para normalizar")
        return 0
    
    print(f"\n🔍 Códigos a normalizar: {len(codes_map)}")
    
    # Mostrar ejemplos
    print("\n📝 Ejemplos de normalización:")
    for i, (original, items) in enumerate(list(codes_map.items())[:5]):
        normalized = items[0]['normalized']
        print(f"   {i+1}. '{original}' → '{normalized}' ({len(items)} registros)")
    
    # Confirmar
    print(f"\n⚠️  Se actualizarán {sum(len(items) for items in codes_map.values())} registros")
    respuesta = input("¿Continuar? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return 0
    
    # Actualizar códigos
    updated = 0
    for original, items in codes_map.items():
        normalized = items[0]['normalized']
        
        for item in items:
            detalle = session.query(CierreMensualUsuario).get(item['id'])
            if detalle:
                detalle.codigo_usuario = normalized
                updated += 1
    
    session.commit()
    print(f"\n✅ {updated} registros actualizados")
    
    return updated

def find_duplicates(session):
    """Busca usuarios duplicados después de la normalización"""
    print("\n" + "="*80)
    print("BUSCANDO DUPLICADOS")
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
    duplicates_contadores = result.fetchall()
    
    # Buscar duplicados en cierre_mensual_usuario
    query2 = text("""
        SELECT 
            cierre_id,
            codigo_usuario,
            nombre_usuario,
            COUNT(*) as count
        FROM cierre_mensual_usuario
        GROUP BY cierre_id, codigo_usuario, nombre_usuario
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """)
    
    result2 = session.execute(query2)
    duplicates_cierres = result2.fetchall()
    
    total_duplicates = len(duplicates_contadores) + len(duplicates_cierres)
    
    if duplicates_contadores:
        print(f"\n⚠️  Duplicados en contadores_usuario: {len(duplicates_contadores)} grupos")
        for dup in duplicates_contadores[:5]:
            print(f"   - Printer {dup[0]}, Código '{dup[1]}', {dup[2]}: {dup[4]} registros")
    
    if duplicates_cierres:
        print(f"\n⚠️  Duplicados en cierre_mensual_usuario: {len(duplicates_cierres)} grupos")
        for dup in duplicates_cierres[:5]:
            print(f"   - Cierre {dup[0]}, Código '{dup[1]}', {dup[2]}: {dup[3]} registros")
    
    if not duplicates_contadores and not duplicates_cierres:
        print("\n✅ No se encontraron duplicados")
    else:
        print("\n💡 Estos duplicados pueden ser del mismo usuario en diferentes fechas")
        print("   o pueden requerir consolidación manual")
    
    return total_duplicates

def main():
    print("="*80)
    print("🔧 SCRIPT DE CORRECCIÓN DE CÓDIGOS DUPLICADOS")
    print("="*80)
    print("\nEste script normalizará los códigos de usuario eliminando ceros al inicio")
    print("Ejemplo: '0455' → '455', '0931' → '931'")
    
    # Crear sesión
    session = next(get_db())
    
    try:
        # Corregir contadores_usuario
        updated_contadores = fix_contadores_usuario(session)
        
        # Corregir cierre_detalle
        updated_detalles = fix_cierre_detalle(session)
        
        # Buscar duplicados restantes
        duplicates = find_duplicates(session)
        
        # Resumen
        print("\n" + "="*80)
        print("RESUMEN")
        print("="*80)
        print(f"\n✅ Registros actualizados en contadores_usuario: {updated_contadores}")
        print(f"✅ Registros actualizados en cierre_detalle: {updated_detalles}")
        print(f"⚠️  Grupos de duplicados encontrados: {duplicates}")
        
        if duplicates > 0:
            print("\n💡 Recomendación: Revisar duplicados manualmente")
        
        print("\n🎉 Corrección completada")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    main()
