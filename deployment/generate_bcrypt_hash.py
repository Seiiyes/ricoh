#!/usr/bin/env python
"""
Utilitario para generar hashes Bcrypt seguros para las contraseñas de auditoría.
Permite configurar el .env con hashes seguros en lugar de contraseñas en texto plano.
"""
import sys
import getpass
try:
    from passlib.context import CryptContext
except ImportError:
    print("Error: Se requiere la librería 'passlib' instalada (pip install passlib[bcrypt]).")
    sys.exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main():
    print("=====================================================================")
    print(" Generador de Hashes Bcrypt para Portal de Auditoría (Puerto 8088)")
    print("=====================================================================")
    
    usuario = input("Ingrese el nombre de usuario de auditoría (ej: admin_dev): ").strip()
    if not usuario:
        print("Error: El nombre de usuario no puede estar vacío.")
        return
        
    password = getpass.getpass("Ingrese la contraseña secreta: ")
    confirm_password = getpass.getpass("Confirme la contraseña: ")
    
    if password != confirm_password:
        print("Error: Las contraseñas no coinciden.")
        return
        
    if len(password) < 8:
        print("Advertencia: Se recomienda una contraseña de al menos 8 caracteres por seguridad.")
        
    # Generar hash
    password_hash = pwd_context.hash(password)
    
    print("\n---------------------------------------------------------------------")
    print(" Hash Bcrypt generado con éxito:")
    print("---------------------------------------------------------------------")
    print(password_hash)
    print("---------------------------------------------------------------------")
    print("\nInstrucciones de Uso:")
    print(f"1. Copie la siguiente línea y agréguela a su archivo '.env' en producción:")
    print(f'   AUDIT_USERS="{usuario}:{password_hash}"')
    print("\n2. Si desea agregar múltiples usuarios, sepárelos por comas. Ejemplo:")
    print(f'   AUDIT_USERS="user1:hash1,user2:hash2"')
    print("=====================================================================")


if __name__ == "__main__":
    main()
