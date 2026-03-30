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
    
    all_ok = True
    
    # Verificar variables de entorno directamente
    encryption_key = os.getenv('ENCRYPTION_KEY')
    secret_key = os.getenv('SECRET_KEY')
    environment = os.getenv('ENVIRONMENT', 'development')
    redis_url = os.getenv('REDIS_URL')
    ricoh_password = os.getenv('RICOH_ADMIN_PASSWORD')
    
    # 1. ENCRYPTION_KEY
    if encryption_key:
        print_success("ENCRYPTION_KEY configurada")
        if len(encryption_key) < 20:
            print_warning("ENCRYPTION_KEY parece muy corta")
            all_ok = False
    else:
        print_error("ENCRYPTION_KEY no configurada")
        all_ok = False
    
    # 2. SECRET_KEY
    if secret_key:
        if len(secret_key) >= 32:
            print_success(f"SECRET_KEY configurada (longitud: {len(secret_key)})")
            
            # Verificar entropía
            import string
            has_upper = any(c in string.ascii_uppercase for c in secret_key)
            has_lower = any(c in string.ascii_lowercase for c in secret_key)
            has_digit = any(c in string.digits for c in secret_key)
            has_special = any(c in string.punctuation for c in secret_key)
            categories = sum([has_upper, has_lower, has_digit, has_special])
            
            if categories >= 3:
                print_success(f"SECRET_KEY tiene entropía suficiente ({categories}/4 categorías)")
            else:
                print_error(f"SECRET_KEY tiene baja entropía ({categories}/4 categorías)")
                all_ok = False
        else:
            print_error(f"SECRET_KEY muy corta (longitud: {len(secret_key)}, mínimo: 32)")
            all_ok = False
    else:
        print_error("SECRET_KEY no configurada")
        all_ok = False
    
    # 3. ENVIRONMENT
    if environment == 'production':
        print_success("ENVIRONMENT=production")
        
        # En producción, CSRF debe estar habilitada
        print_info("CSRF se habilita automáticamente en producción")
        
        # Verificar HTTPS
        force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
        if force_https:
            print_success("FORCE_HTTPS habilitado")
        else:
            print_warning("FORCE_HTTPS deshabilitado (recomendado habilitarlo)")
    else:
        print_info(f"ENVIRONMENT={environment} (no producción)")
    
    # 4. REDIS_URL (requerido para producción)
    if redis_url:
        print_success("REDIS_URL configurada (almacenamiento distribuido)")
    else:
        if environment == 'production':
            print_warning("REDIS_URL no configurada (recomendado para producción)")
        else:
            print_info("REDIS_URL no configurada (usando memoria en desarrollo)")
    
    # 5. RICOH_ADMIN_PASSWORD
    if ricoh_password:
        print_success("RICOH_ADMIN_PASSWORD configurada")
    else:
        print_warning("RICOH_ADMIN_PASSWORD no configurada (requerida para integración con impresoras)")
    
    # 6. DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print_success("DATABASE_URL configurada")
        
        # Verificar que no tiene credenciales hardcodeadas
        if 'ricoh_secure_2024' in database_url:
            print_error("DATABASE_URL contiene credenciales hardcodeadas de desarrollo")
            all_ok = False
    else:
        print_error("DATABASE_URL no configurada")
        all_ok = False
    
    return all_ok

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
