#!/usr/bin/env python3
"""
Script para inicializar el superadmin con contraseña segura
Genera una contraseña temporal aleatoria y la hashea con bcrypt

Uso:
    python backend/scripts/init_superadmin.py
"""

import os
import sys
import secrets
import string
from pathlib import Path

# Agregar el directorio backend al path para importar módulos
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

try:
    import bcrypt
    from sqlalchemy import create_engine, text
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Error: Falta instalar dependencias: {e}")
    print("   Ejecutar: pip install bcrypt sqlalchemy python-dotenv psycopg2-binary")
    sys.exit(1)


def generate_secure_password(length: int = 16) -> str:
    """
    Genera una contraseña aleatoria segura
    
    Requisitos:
    - Mínimo 16 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    
    Args:
        length: Longitud de la contraseña (default: 16)
        
    Returns:
        str: Contraseña segura generada
    """
    if length < 16:
        length = 16
    
    # Definir conjuntos de caracteres
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    # Asegurar al menos un carácter de cada tipo
    password_chars = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Completar con caracteres aleatorios
    all_chars = uppercase + lowercase + digits + special
    password_chars.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Mezclar aleatoriamente
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt con 12 rounds
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash bcrypt de la contraseña
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def update_superadmin_password(database_url: str, password_hash: str) -> bool:
    """
    Actualiza el password_hash del superadmin en la base de datos
    
    Args:
        database_url: URL de conexión a PostgreSQL
        password_hash: Hash bcrypt de la contraseña
        
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Actualizar password_hash del superadmin
            result = conn.execute(
                text("""
                    UPDATE admin_users 
                    SET password_hash = :password_hash,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE username = 'superadmin'
                """),
                {"password_hash": password_hash}
            )
            conn.commit()
            
            if result.rowcount == 0:
                print("❌ Error: Usuario 'superadmin' no encontrado en la base de datos")
                print("   Asegúrate de haber ejecutado la migración 011 primero")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return False


def main():
    """Función principal"""
    print("=" * 80)
    print("🔐 Inicialización de Superadmin - Ricoh Suite")
    print("=" * 80)
    print()
    
    # Cargar variables de entorno (priorizar .env.local para desarrollo local)
    env_local = backend_dir / '.env.local'
    env_file = backend_dir / '.env'
    
    if env_local.exists():
        load_dotenv(env_local)
        print(f"✅ Variables de entorno cargadas desde: .env.local")
    elif env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Variables de entorno cargadas desde: .env")
    else:
        print(f"⚠️  Archivos .env no encontrados")
        print("   Usando variables de entorno del sistema")
    
    # Obtener DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ Error: Variable de entorno DATABASE_URL no configurada")
        print("   Configurar en .env o como variable de entorno del sistema")
        print("   Ejemplo: DATABASE_URL=postgresql://user:password@localhost:5432/ricoh_db")
        sys.exit(1)
    
    print(f"✅ DATABASE_URL configurada")
    print()
    
    # Generar contraseña temporal
    print("🔑 Generando contraseña temporal segura...")
    temp_password = generate_secure_password(16)
    print(f"✅ Contraseña generada: {len(temp_password)} caracteres")
    print()
    
    # Hashear contraseña
    print("🔒 Hasheando contraseña con bcrypt (12 rounds)...")
    password_hash = hash_password(temp_password)
    print(f"✅ Hash generado: {len(password_hash)} caracteres")
    print()
    
    # Actualizar en base de datos
    print("💾 Actualizando contraseña en base de datos...")
    if update_superadmin_password(database_url, password_hash):
        print("✅ Contraseña actualizada exitosamente")
        print()
        print("=" * 80)
        print("🎉 SUPERADMIN INICIALIZADO CORRECTAMENTE")
        print("=" * 80)
        print()
        print("📋 CREDENCIALES DE ACCESO:")
        print(f"   Username: superadmin")
        print(f"   Password: {temp_password}")
        print()
        print("⚠️  IMPORTANTE:")
        print("   1. Guarda esta contraseña en un lugar seguro")
        print("   2. Cambia la contraseña en el primer login")
        print("   3. Esta contraseña NO se mostrará nuevamente")
        print()
        print("🌐 Acceso al sistema:")
        print("   URL: http://localhost:5173/login (frontend)")
        print("   API: http://localhost:8000/docs (Swagger)")
        print()
        print("=" * 80)
    else:
        print("❌ Error al actualizar contraseña")
        sys.exit(1)


if __name__ == "__main__":
    main()
