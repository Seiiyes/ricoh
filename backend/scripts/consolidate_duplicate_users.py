#!/usr/bin/env python3
"""
Script para consolidar usuarios duplicados.
Normaliza códigos de usuario y consolida registros duplicados.

IMPORTANTE: Este script debe ejecutarse ANTES de agregar el constraint UNIQUE.
"""
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.database import get_db
from db.models import User, ContadorUsuario, CierreMensualUsuario, UserPrinterAssignment
from datetime import datetime
from typing import Dict, List, Tuple

def normalize_user_code(code: str) -> str:
    """
    Normaliza código de usuario eliminando ceros a la izquierda.
    
    Args:
        code: Código de usuario (puede tener ceros a la izquierda)
    
    Returns:
        Código normalizado sin ceros a la izquierda
    
    Examples:
        "0547" → "547"
        "8599" → "8599"
        "0000" → "0"
    """
    if not code or not code.strip():
        return "0"
    
    normalized = code.strip().lstrip('0')
    return normalized if normalized else "0"

def find_duplicate_groups(session) -> Dict[str, List[User]]:
    """
    Encuentra grupos de usuarios que tienen el mismo código normalizado.
    
    Returns:
        Dict donde la clave es el código normalizado y el valor es lista de usuarios
    """
    print("\n" + "="*80)
    print("🔍 BUSCANDO USUARIOS DUPLICADOS")
    print("="*80)
    
    # Obtener todos los usuarios
    all_users = session.query(User).all()
    print(f"\n📊 Total de usuarios en BD: {len(all_users)}")
    
    # Agrupar por código normalizado
    groups = {}
    for user in all_users:
        normalized = normalize_user_code(user.codigo_de_usuario)
        
        if normalized not in groups:
            groups[normalized] = []
        groups[normalized].append(user)
    
    # Filtrar solo grupos con duplicados
    duplicate_groups = {k: v for k, v in groups.items() if len(v) > 1}
    
    print(f"⚠️  Grupos de duplicados encontrados: {len(duplicate_groups)}")
    
    if duplicate_groups:
        print("\n📝 Ejemplos de duplicados:")
        for i, (normalized, users) in enumerate(list(duplicate_groups.items())[:10]):
            print(f"\n   {i+1}. Código normalizado: '{normalized}' ({len(users)} usuarios)")
            for user in users:
                print(f"      - ID {user.id}: {user.name} (código: '{user.codigo_de_usuario}')")
    
    return duplicate_groups

def select_primary_user(users: List[User]) -> User:
    """
    Selecciona el usuario "principal" de un grupo de duplicados.
    Criterios:
    1. Usuario con código ya normalizado (sin ceros a la izquierda)
    2. Usuario más antiguo (created_at)
    3. Usuario con más asignaciones de impresoras
    
    Args:
        users: Lista de usuarios duplicados
    
    Returns:
        Usuario seleccionado como principal
    """
    # Criterio 1: Preferir usuario con código ya normalizado
    for user in users:
        normalized = normalize_user_code(user.codigo_de_usuario)
        if user.codigo_de_usuario == normalized:
            return user
    
    # Criterio 2: Usuario más antiguo
    users_sorted = sorted(users, key=lambda u: u.created_at or datetime.min)
    return users_sorted[0]

def consolidate_user_group(session, normalized_code: str, users: List[User]) -> Tuple[int, int]:
    """
    Consolida un grupo de usuarios duplicados.
    
    Args:
        session: Sesión de base de datos
        normalized_code: Código normalizado del grupo
        users: Lista de usuarios duplicados
    
    Returns:
        Tupla (usuarios_eliminados, referencias_actualizadas)
    """
    if len(users) <= 1:
        return (0, 0)
    
    # Seleccionar usuario principal
    primary_user = select_primary_user(users)
    duplicate_users = [u for u in users if u.id != primary_user.id]
    
    print(f"\n   → Usuario principal: ID {primary_user.id} - {primary_user.name} ('{primary_user.codigo_de_usuario}')")
    print(f"   → Usuarios a consolidar: {[f'ID {u.id}' for u in duplicate_users]}")
    
    # Actualizar código del usuario principal si no está normalizado
    if primary_user.codigo_de_usuario != normalized_code:
        print(f"   → Normalizando código principal: '{primary_user.codigo_de_usuario}' → '{normalized_code}'")
        primary_user.codigo_de_usuario = normalized_code
    
    referencias_actualizadas = 0
    
    # Actualizar referencias en todas las tablas
    for dup_user in duplicate_users:
        print(f"   → Consolidando ID {dup_user.id} → ID {primary_user.id}")
        
        # 1. Actualizar contadores_usuario
        contadores = session.query(ContadorUsuario).filter(
            ContadorUsuario.user_id == dup_user.id
        ).all()
        for contador in contadores:
            contador.user_id = primary_user.id
            referencias_actualizadas += 1
        
        # 2. Actualizar cierre_mensual_usuario
        cierres = session.query(CierreMensualUsuario).filter(
            CierreMensualUsuario.user_id == dup_user.id
        ).all()
        for cierre in cierres:
            cierre.user_id = primary_user.id
            referencias_actualizadas += 1
        
        # 3. Actualizar user_printer_assignments
        assignments = session.query(UserPrinterAssignment).filter(
            UserPrinterAssignment.user_id == dup_user.id
        ).all()
        for assignment in assignments:
            # Verificar si ya existe asignación para el usuario principal
            existing = session.query(UserPrinterAssignment).filter(
                UserPrinterAssignment.user_id == primary_user.id,
                UserPrinterAssignment.printer_id == assignment.printer_id
            ).first()
            
            if existing:
                # Ya existe, eliminar duplicado
                session.delete(assignment)
            else:
                # No existe, actualizar a usuario principal
                assignment.user_id = primary_user.id
                referencias_actualizadas += 1
        
        # 4. Eliminar usuario duplicado
        session.delete(dup_user)
    
    session.flush()
    
    return (len(duplicate_users), referencias_actualizadas)

def consolidate_all_duplicates(session) -> Dict[str, int]:
    """
    Consolida todos los usuarios duplicados.
    
    Returns:
        Dict con estadísticas de consolidación
    """
    print("\n" + "="*80)
    print("🔧 CONSOLIDANDO USUARIOS DUPLICADOS")
    print("="*80)
    
    # Encontrar grupos de duplicados
    duplicate_groups = find_duplicate_groups(session)
    
    if not duplicate_groups:
        print("\n✅ No hay usuarios duplicados para consolidar")
        return {
            "grupos_procesados": 0,
            "usuarios_eliminados": 0,
            "referencias_actualizadas": 0
        }
    
    # Confirmar consolidación
    print(f"\n⚠️  Se consolidarán {len(duplicate_groups)} grupos de usuarios duplicados")
    print("⚠️  Esta operación actualizará referencias en:")
    print("   - contadores_usuario")
    print("   - cierre_mensual_usuario")
    print("   - user_printer_assignments")
    print("   - users (eliminará duplicados)")
    
    # Auto-confirmar en modo no interactivo
    import sys
    if not sys.stdin.isatty():
        print("\n✓ Modo no interactivo: Auto-confirmando consolidación")
        respuesta = 's'
    else:
        respuesta = input("\n¿Continuar con la consolidación? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return {
            "grupos_procesados": 0,
            "usuarios_eliminados": 0,
            "referencias_actualizadas": 0
        }
    
    # Consolidar cada grupo
    total_eliminados = 0
    total_referencias = 0
    grupos_procesados = 0
    
    for normalized_code, users in duplicate_groups.items():
        print(f"\n📦 Procesando grupo: código '{normalized_code}' ({len(users)} usuarios)")
        
        try:
            eliminados, referencias = consolidate_user_group(session, normalized_code, users)
            total_eliminados += eliminados
            total_referencias += referencias
            grupos_procesados += 1
            
            print(f"   ✅ Grupo consolidado: {eliminados} usuarios eliminados, {referencias} referencias actualizadas")
            
        except Exception as e:
            print(f"   ❌ Error al consolidar grupo: {e}")
            session.rollback()
            raise
    
    # Commit final
    session.commit()
    
    print("\n" + "="*80)
    print("✅ CONSOLIDACIÓN COMPLETADA")
    print("="*80)
    print(f"\n📊 Estadísticas:")
    print(f"   - Grupos procesados: {grupos_procesados}")
    print(f"   - Usuarios eliminados: {total_eliminados}")
    print(f"   - Referencias actualizadas: {total_referencias}")
    
    return {
        "grupos_procesados": grupos_procesados,
        "usuarios_eliminados": total_eliminados,
        "referencias_actualizadas": total_referencias
    }

def verify_no_duplicates(session) -> bool:
    """
    Verifica que no queden usuarios duplicados después de la consolidación.
    
    Returns:
        True si no hay duplicados, False si aún hay duplicados
    """
    print("\n" + "="*80)
    print("✓ VERIFICANDO CONSOLIDACIÓN")
    print("="*80)
    
    duplicate_groups = find_duplicate_groups(session)
    
    if not duplicate_groups:
        print("\n✅ Verificación exitosa: No hay usuarios duplicados")
        return True
    else:
        print(f"\n❌ Verificación fallida: Aún hay {len(duplicate_groups)} grupos de duplicados")
        return False

def main():
    print("="*80)
    print("🔧 SCRIPT DE CONSOLIDACIÓN DE USUARIOS DUPLICADOS")
    print("="*80)
    print("\nEste script:")
    print("1. Identifica usuarios con códigos que normalizan al mismo valor")
    print("2. Selecciona un usuario 'principal' por grupo")
    print("3. Actualiza todas las referencias FK al usuario principal")
    print("4. Elimina usuarios duplicados")
    print("5. Normaliza códigos de usuario (elimina ceros a la izquierda)")
    
    # Crear sesión
    session = next(get_db())
    
    try:
        # Consolidar duplicados
        stats = consolidate_all_duplicates(session)
        
        # Verificar que no queden duplicados
        if stats["grupos_procesados"] > 0:
            verify_no_duplicates(session)
        
        # Resumen final
        print("\n" + "="*80)
        print("📋 RESUMEN FINAL")
        print("="*80)
        print(f"\n✅ Grupos consolidados: {stats['grupos_procesados']}")
        print(f"✅ Usuarios eliminados: {stats['usuarios_eliminados']}")
        print(f"✅ Referencias actualizadas: {stats['referencias_actualizadas']}")
        
        if stats["grupos_procesados"] > 0:
            print("\n💡 Siguiente paso:")
            print("   Ejecutar migración 016 para agregar constraint UNIQUE:")
            print("   docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -f /app/migrations/016_fix_duplicate_users.sql")
        
        print("\n🎉 Consolidación completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante consolidación: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
