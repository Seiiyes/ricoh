#!/usr/bin/env python3
"""
Script para CORREGIR códigos de usuario agregando ceros a la izquierda.
Los códigos de usuario en Ricoh son de 4 dígitos con formato fijo.

IMPORTANTE: Este script REVIERTE la normalización incorrecta que eliminó ceros.
"""
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from db.database import get_db
from db.models import User

def fix_user_code_format(code: str) -> str:
    """
    Formatea código de usuario a 4 dígitos con ceros a la izquierda.
    
    Args:
        code: Código de usuario (puede estar sin ceros)
    
    Returns:
        Código formateado a 4 dígitos
    
    Examples:
        "547" → "0547"
        "8599" → "8599" (ya tiene 4 dígitos)
        "37" → "0037"
    """
    if not code or not code.strip():
        return "0000"
    
    # Eliminar espacios y rellenar con ceros a la izquierda hasta 4 dígitos
    code_clean = code.strip()
    
    # Si el código tiene más de 4 dígitos, dejarlo como está
    if len(code_clean) > 4:
        return code_clean
    
    # Rellenar con ceros a la izquierda hasta 4 dígitos
    return code_clean.zfill(4)

def fix_all_user_codes(session: Session):
    """
    Corrige todos los códigos de usuario agregando ceros a la izquierda.
    """
    print("\n" + "="*80)
    print("🔧 CORRIGIENDO CÓDIGOS DE USUARIO")
    print("="*80)
    print("\nLos códigos de usuario en Ricoh son de 4 dígitos con formato fijo.")
    print("Este script agregará ceros a la izquierda donde sea necesario.")
    
    # Obtener todos los usuarios
    users = session.query(User).all()
    print(f"\n📊 Total de usuarios: {len(users)}")
    
    # Identificar usuarios que necesitan corrección
    users_to_fix = []
    for user in users:
        original_code = user.codigo_de_usuario
        fixed_code = fix_user_code_format(original_code)
        
        if original_code != fixed_code:
            users_to_fix.append({
                'id': user.id,
                'name': user.name,
                'original': original_code,
                'fixed': fixed_code
            })
    
    if not users_to_fix:
        print("\n✅ Todos los códigos ya tienen el formato correcto (4 dígitos)")
        return 0
    
    print(f"\n⚠️  Usuarios que necesitan corrección: {len(users_to_fix)}")
    
    # Mostrar ejemplos
    print("\n📝 Ejemplos de corrección:")
    for i, user_info in enumerate(users_to_fix[:10]):
        print(f"   {i+1}. ID {user_info['id']}: {user_info['name']}")
        print(f"      '{user_info['original']}' → '{user_info['fixed']}'")
    
    if len(users_to_fix) > 10:
        print(f"   ... y {len(users_to_fix) - 10} más")
    
    # Confirmar
    print(f"\n⚠️  Se actualizarán {len(users_to_fix)} códigos de usuario")
    
    # Auto-confirmar en modo no interactivo
    import sys
    if not sys.stdin.isatty():
        print("\n✓ Modo no interactivo: Auto-confirmando corrección")
        respuesta = 's'
    else:
        respuesta = input("\n¿Continuar con la corrección? (s/n): ")
    
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        return 0
    
    # Aplicar correcciones
    updated = 0
    for user_info in users_to_fix:
        user = session.query(User).filter(User.id == user_info['id']).first()
        if user:
            user.codigo_de_usuario = user_info['fixed']
            updated += 1
            
            if updated % 50 == 0:
                session.commit()
                print(f"   Progreso: {updated}/{len(users_to_fix)} usuarios actualizados...")
    
    session.commit()
    
    print(f"\n✅ {updated} códigos de usuario corregidos")
    
    return updated

def verify_codes(session: Session):
    """
    Verifica que todos los códigos tengan el formato correcto.
    """
    print("\n" + "="*80)
    print("✓ VERIFICANDO CÓDIGOS")
    print("="*80)
    
    # Contar códigos por longitud
    from sqlalchemy import func
    
    length_counts = session.query(
        func.length(User.codigo_de_usuario).label('len'),
        func.count().label('count')
    ).group_by('len').order_by('len').all()
    
    print("\n📊 Distribución de longitudes de códigos:")
    for length, count in length_counts:
        print(f"   {length} dígitos: {count} usuarios")
    
    # Verificar si hay códigos con menos de 4 dígitos
    short_codes = session.query(User).filter(
        func.length(User.codigo_de_usuario) < 4
    ).count()
    
    if short_codes == 0:
        print("\n✅ Verificación exitosa: Todos los códigos tienen 4 o más dígitos")
        return True
    else:
        print(f"\n⚠️  Aún hay {short_codes} códigos con menos de 4 dígitos")
        return False

def main():
    print("="*80)
    print("🔧 SCRIPT DE CORRECCIÓN DE CÓDIGOS DE USUARIO")
    print("="*80)
    print("\nEste script corrige códigos de usuario agregando ceros a la izquierda.")
    print("Los códigos de usuario en Ricoh son de 4 dígitos con formato fijo.")
    print("\nEjemplos:")
    print("  '547' → '0547'")
    print("  '37' → '0037'")
    print("  '8599' → '8599' (sin cambios)")
    
    # Crear sesión
    session = next(get_db())
    
    try:
        # Corregir códigos
        updated = fix_all_user_codes(session)
        
        # Verificar corrección
        if updated > 0:
            verify_codes(session)
        
        # Resumen
        print("\n" + "="*80)
        print("📋 RESUMEN")
        print("="*80)
        print(f"\n✅ Códigos corregidos: {updated}")
        
        if updated > 0:
            print("\n💡 Siguiente paso:")
            print("   Verificar que los códigos ahora coinciden con los de las impresoras")
            print("   Leer contadores de una impresora para verificar")
        
        print("\n🎉 Corrección completada")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main()
