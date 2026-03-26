#!/usr/bin/env python3
"""
Script de Verificación de Despliegue
Verifica que todos los componentes estén configurados correctamente
"""
import os
import sys
from pathlib import Path

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_env_file():
    """Verificar que existe .env y tiene las variables necesarias"""
    print_header("Verificando Archivo .env")
    
    env_path = Path(".env")
    if not env_path.exists():
        print_error(".env no encontrado")
        print_info("Copia .env.example a .env y configúralo")
        return False
    
    print_success(".env encontrado")
    
    # Leer variables
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY",
        "ENCRYPTION_KEY",
        "ENVIRONMENT"
    ]
    
    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    all_ok = True
    for var in required_vars:
        if var in env_vars and env_vars[var]:
            print_success(f"{var} configurado")
        else:
            print_error(f"{var} no configurado o vacío")
            all_ok = False
    
    # Verificar longitud de SECRET_KEY
    if 'SECRET_KEY' in env_vars:
        if len(env_vars['SECRET_KEY']) < 32:
            print_warning("SECRET_KEY debería tener al menos 32 caracteres")
            all_ok = False
    
    # Verificar ENCRYPTION_KEY
    if 'ENCRYPTION_KEY' in env_vars:
        if len(env_vars['ENCRYPTION_KEY']) < 20:
            print_warning("ENCRYPTION_KEY parece inválida")
            all_ok = False
    
    return all_ok

def check_database_connection():
    """Verificar conexión a base de datos"""
    print_header("Verificando Conexión a Base de Datos")
    
    try:
        from db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print_success("Conexión a base de datos exitosa")
        return True
    except Exception as e:
        print_error(f"Error conectando a base de datos: {e}")
        return False

def check_tables():
    """Verificar que las tablas existen"""
    print_header("Verificando Tablas de Base de Datos")
    
    try:
        from db.database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'empresas',
            'admin_users',
            'admin_sessions',
            'admin_audit_log',
            'users',
            'printers',
            'user_printer_assignments'
        ]
        
        all_ok = True
        for table in required_tables:
            if table in tables:
                print_success(f"Tabla '{table}' existe")
            else:
                print_error(f"Tabla '{table}' no encontrada")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print_error(f"Error verificando tablas: {e}")
        return False

def check_encryption_service():
    """Verificar que el servicio de encriptación funciona"""
    print_header("Verificando Servicio de Encriptación")
    
    try:
        from services.encryption_service import EncryptionService
        
        # Test de encriptación/desencriptación
        test_data = "test_password_123"
        encrypted = EncryptionService.encrypt(test_data)
        decrypted = EncryptionService.decrypt(encrypted)
        
        if decrypted == test_data:
            print_success("Servicio de encriptación funciona correctamente")
            return True
        else:
            print_error("Error en encriptación/desencriptación")
            return False
    except Exception as e:
        print_error(f"Error en servicio de encriptación: {e}")
        return False

def check_sanitization_service():
    """Verificar que el servicio de sanitización funciona"""
    print_header("Verificando Servicio de Sanitización")
    
    try:
        from services.sanitization_service import SanitizationService
        
        # Test de sanitización
        malicious = '<script>alert("XSS")</script>'
        sanitized = SanitizationService.sanitize_string(malicious)
        
        if '<script>' not in sanitized:
            print_success("Servicio de sanitización funciona correctamente")
            return True
        else:
            print_error("Error en sanitización")
            return False
    except Exception as e:
        print_error(f"Error en servicio de sanitización: {e}")
        return False

def check_jwt_service():
    """Verificar que el servicio JWT funciona"""
    print_header("Verificando Servicio JWT")
    
    try:
        from services.jwt_service import JWTService
        from unittest.mock import Mock
        
        # Crear mock user
        user = Mock()
        user.id = 1
        user.username = "test"
        user.rol = "admin"
        user.empresa_id = 1
        
        # Test de creación de token
        token = JWTService.create_access_token(user)
        
        # Test de decodificación
        payload = JWTService.decode_token(token)
        
        if payload['user_id'] == 1 and payload['username'] == 'test':
            print_success("Servicio JWT funciona correctamente")
            return True
        else:
            print_error("Error en JWT")
            return False
    except Exception as e:
        print_error(f"Error en servicio JWT: {e}")
        return False

def check_dependencies():
    """Verificar que las dependencias están instaladas"""
    print_header("Verificando Dependencias")
    
    required_packages = [
        'fastapi',
        'sqlalchemy',
        'psycopg2',
        'cryptography',
        'bcrypt',
        'pyjwt',
        'uvicorn'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} instalado")
        except ImportError:
            print_error(f"{package} no instalado")
            all_ok = False
    
    return all_ok

def check_security_config():
    """Verificar configuración de seguridad"""
    print_header("Verificando Configuración de Seguridad")
    
    env_vars = {}
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Verificar ENVIRONMENT
    environment = env_vars.get('ENVIRONMENT', 'development')
    if environment == 'production':
        print_success("ENVIRONMENT=production")
        
        # En producción, verificar configuraciones adicionales
        if env_vars.get('FORCE_HTTPS', 'false').lower() == 'true':
            print_success("FORCE_HTTPS habilitado")
        else:
            print_warning("FORCE_HTTPS deshabilitado (recomendado habilitarlo con SSL)")
        
        if env_vars.get('ENABLE_CSRF', 'false').lower() == 'true':
            print_success("CSRF Protection habilitado")
        else:
            print_info("CSRF Protection deshabilitado (opcional)")
    else:
        print_info(f"ENVIRONMENT={environment} (desarrollo)")
    
    return True

def main():
    """Ejecutar todas las verificaciones"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{'VERIFICACIÓN DE DESPLIEGUE':^60}{RESET}")
    print(f"{BLUE}{'Ricoh Equipment Management Suite':^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {
        "Archivo .env": check_env_file(),
        "Dependencias": check_dependencies(),
        "Conexión BD": check_database_connection(),
        "Tablas BD": check_tables(),
        "Servicio Encriptación": check_encryption_service(),
        "Servicio Sanitización": check_sanitization_service(),
        "Servicio JWT": check_jwt_service(),
        "Configuración Seguridad": check_security_config()
    }
    
    # Resumen
    print_header("Resumen de Verificación")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}: OK")
        else:
            print_error(f"{check}: FALLO")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}✅ Todas las verificaciones pasaron ({passed}/{total}){RESET}")
        print(f"{GREEN}🎉 Sistema listo para producción{RESET}")
        return 0
    else:
        print(f"{RED}❌ {total - passed} verificaciones fallaron ({passed}/{total}){RESET}")
        print(f"{YELLOW}⚠️  Corrige los errores antes de desplegar{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
