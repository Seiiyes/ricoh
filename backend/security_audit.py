#!/usr/bin/env python3
"""
Security Audit Script
Verifica la configuración de seguridad del sistema
"""
import os
import sys
import re
from pathlib import Path

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_environment():
    """Check ENVIRONMENT variable"""
    print_header("1. Verificando Variable ENVIRONMENT")
    
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        print_success(f"ENVIRONMENT = {env}")
        return True
    elif env == 'development':
        print_warning(f"ENVIRONMENT = {env}")
        print_warning("   Esto es correcto para desarrollo local")
        print_warning("   CAMBIAR a 'production' antes de desplegar")
        return False
    else:
        print_error(f"ENVIRONMENT = {env} (valor inválido)")
        return False

def check_debug():
    """Check DEBUG variable"""
    print_header("2. Verificando Variable DEBUG")
    
    debug = os.getenv('DEBUG', 'true').lower()
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production' and debug == 'true':
        print_error(f"DEBUG = {debug}")
        print_error("   ¡PELIGRO! DEBUG debe ser 'false' en producción")
        print_error("   Expone información sensible en errores")
        return False
    elif env == 'production' and debug == 'false':
        print_success(f"DEBUG = {debug}")
        return True
    elif env == 'development':
        print_warning(f"DEBUG = {debug}")
        print_warning("   Esto es correcto para desarrollo")
        return True
    else:
        print_warning(f"DEBUG = {debug}")
        return True

def check_encryption_key():
    """Check ENCRYPTION_KEY"""
    print_header("3. Verificando ENCRYPTION_KEY")
    
    key = os.getenv('ENCRYPTION_KEY', '')
    
    if not key:
        print_error("ENCRYPTION_KEY no configurada")
        return False
    
    # Check if it's the example key
    if key == 'ynVBzh9ZjawHMoUHu0L9ozXT2j8ebujlVxoNzD91xjE=':
        print_error("ENCRYPTION_KEY es la clave de ejemplo")
        print_error("   ¡PELIGRO! Generar una nueva clave única")
        print_error("   Comando: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        return False
    
    if 'example' in key.lower() or 'change' in key.lower():
        print_error("ENCRYPTION_KEY contiene texto de ejemplo")
        return False
    
    if len(key) < 32:
        print_error(f"ENCRYPTION_KEY muy corta ({len(key)} chars)")
        return False
    
    print_success(f"ENCRYPTION_KEY configurada ({len(key)} chars)")
    return True

def check_secret_key():
    """Check SECRET_KEY"""
    print_header("4. Verificando SECRET_KEY")
    
    key = os.getenv('SECRET_KEY', '')
    
    if not key:
        print_error("SECRET_KEY no configurada")
        return False
    
    # Check if it's the example key
    if 'ricoh-jwt-secret-key-change-in-production' in key:
        print_error("SECRET_KEY es la clave de ejemplo")
        print_error("   ¡PELIGRO! Generar una nueva clave única")
        print_error("   Comando: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        return False
    
    if 'example' in key.lower() or 'change' in key.lower():
        print_error("SECRET_KEY contiene texto de ejemplo")
        return False
    
    if len(key) < 32:
        print_error(f"SECRET_KEY muy corta ({len(key)} chars)")
        return False
    
    # Check entropy
    has_upper = any(c.isupper() for c in key)
    has_lower = any(c.islower() for c in key)
    has_digit = any(c.isdigit() for c in key)
    has_special = any(not c.isalnum() for c in key)
    
    entropy_count = sum([has_upper, has_lower, has_digit, has_special])
    
    if entropy_count < 3:
        print_warning(f"SECRET_KEY tiene baja entropía ({entropy_count}/4 tipos de caracteres)")
        print_warning("   Recomendado: al menos 3 de: mayúsculas, minúsculas, dígitos, especiales")
    
    print_success(f"SECRET_KEY configurada ({len(key)} chars, entropía: {entropy_count}/4)")
    return True

def check_cors():
    """Check CORS_ORIGINS"""
    print_header("5. Verificando CORS_ORIGINS")
    
    cors = os.getenv('CORS_ORIGINS', '')
    env = os.getenv('ENVIRONMENT', 'development')
    
    if not cors:
        print_error("CORS_ORIGINS no configurada")
        return False
    
    if cors == '*':
        if env == 'production':
            print_error("CORS_ORIGINS = * (permite todos los orígenes)")
            print_error("   ¡PELIGRO! Restringir a dominios específicos en producción")
            return False
        else:
            print_warning("CORS_ORIGINS = * (permite todos los orígenes)")
            print_warning("   Esto es aceptable para desarrollo")
            print_warning("   CAMBIAR a dominios específicos en producción")
            return True
    
    origins = [o.strip() for o in cors.split(',')]
    
    # Check for localhost in production
    if env == 'production':
        localhost_origins = [o for o in origins if 'localhost' in o or '127.0.0.1' in o]
        if localhost_origins:
            print_warning(f"CORS_ORIGINS contiene localhost en producción: {localhost_origins}")
            print_warning("   Remover orígenes localhost en producción")
    
    # Check for HTTPS
    if env == 'production':
        http_origins = [o for o in origins if o.startswith('http://') and 'localhost' not in o]
        if http_origins:
            print_warning(f"CORS_ORIGINS contiene HTTP (no HTTPS): {http_origins}")
            print_warning("   Usar HTTPS en producción")
    
    print_success(f"CORS_ORIGINS configurada ({len(origins)} origen(es))")
    for origin in origins:
        print(f"   - {origin}")
    
    return True

def check_redis():
    """Check Redis configuration"""
    print_header("6. Verificando Configuración de Redis")
    
    redis_url = os.getenv('REDIS_URL', '')
    redis_password = os.getenv('REDIS_PASSWORD', '')
    env = os.getenv('ENVIRONMENT', 'development')
    
    if not redis_url and not redis_password:
        print_warning("Redis sin contraseña")
        if env == 'production':
            print_error("   ¡PELIGRO! Configurar contraseña en producción")
            return False
        else:
            print_warning("   Aceptable para desarrollo local")
            return True
    
    # Check if password is in URL
    if redis_url and ':@' in redis_url:
        print_warning("Redis URL contiene contraseña vacía (:@)")
        if env == 'production':
            print_error("   ¡PELIGRO! Configurar contraseña en producción")
            return False
    
    if redis_password:
        if len(redis_password) < 16:
            print_warning(f"Redis password corta ({len(redis_password)} chars)")
            print_warning("   Recomendado: al menos 16 caracteres")
        else:
            print_success(f"Redis password configurada ({len(redis_password)} chars)")
    
    if redis_url:
        # Mask password in URL
        masked_url = re.sub(r':([^@]+)@', ':***@', redis_url)
        print_success(f"REDIS_URL configurada: {masked_url}")
    
    return True

def check_database():
    """Check database configuration"""
    print_header("7. Verificando Configuración de Base de Datos")
    
    db_url = os.getenv('DATABASE_URL', '')
    
    if not db_url:
        print_error("DATABASE_URL no configurada")
        return False
    
    # Extract password from URL
    match = re.search(r':([^@]+)@', db_url)
    if match:
        password = match.group(1)
        
        # Check for example passwords
        if password in ['ricoh_secure_2024', 'password', 'admin', '123456']:
            print_error(f"DATABASE_URL usa contraseña de ejemplo: {password}")
            print_error("   ¡PELIGRO! Cambiar a contraseña segura")
            return False
        
        if len(password) < 12:
            print_warning(f"Database password corta ({len(password)} chars)")
            print_warning("   Recomendado: al menos 12 caracteres")
        else:
            print_success(f"Database password configurada ({len(password)} chars)")
    
    # Mask password in URL
    masked_url = re.sub(r':([^@]+)@', ':***@', db_url)
    print_success(f"DATABASE_URL configurada: {masked_url}")
    
    return True

def check_ricoh_password():
    """Check Ricoh admin password"""
    print_header("8. Verificando Contraseña de Ricoh")
    
    password = os.getenv('RICOH_ADMIN_PASSWORD', '')
    
    if not password:
        print_warning("RICOH_ADMIN_PASSWORD no configurada")
        print_warning("   Configurar antes de usar aprovisionamiento")
        return True
    
    if len(password) < 8:
        print_warning(f"RICOH_ADMIN_PASSWORD corta ({len(password)} chars)")
        print_warning("   Recomendado: al menos 8 caracteres")
    else:
        print_success(f"RICOH_ADMIN_PASSWORD configurada ({len(password)} chars)")
    
    return True

def check_https():
    """Check HTTPS configuration"""
    print_header("9. Verificando Configuración HTTPS")
    
    force_https = os.getenv('FORCE_HTTPS', 'false').lower()
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production' and force_https != 'true':
        print_warning("FORCE_HTTPS no habilitado en producción")
        print_warning("   Recomendado: FORCE_HTTPS=true")
        return False
    elif env == 'production':
        print_success("FORCE_HTTPS habilitado")
        return True
    else:
        print_info("FORCE_HTTPS no requerido en desarrollo")
        return True

def check_log_level():
    """Check log level"""
    print_header("10. Verificando Nivel de Logs")
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production' and log_level == 'DEBUG':
        print_warning("LOG_LEVEL=DEBUG en producción")
        print_warning("   Recomendado: INFO o WARNING")
        return False
    elif env == 'production' and log_level in ['INFO', 'WARNING', 'ERROR']:
        print_success(f"LOG_LEVEL = {log_level}")
        return True
    else:
        print_info(f"LOG_LEVEL = {log_level}")
        return True

def print_summary(results):
    """Print summary"""
    print_header("RESUMEN DE AUDITORÍA DE SEGURIDAD")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total de verificaciones: {total}")
    print(f"Exitosas: {GREEN}{passed}{RESET}")
    print(f"Fallidas: {RED}{failed}{RESET}")
    print(f"Porcentaje: {(passed/total*100):.1f}%\n")
    
    env = os.getenv('ENVIRONMENT', 'development')
    
    if env == 'production':
        if passed == total:
            print_success("✅ TODAS LAS VERIFICACIONES PASARON")
            print(f"\n{GREEN}El sistema está listo para producción{RESET}\n")
            return True
        else:
            print_error("❌ ALGUNAS VERIFICACIONES FALLARON")
            print(f"\n{RED}Corregir los errores antes de desplegar en producción{RESET}\n")
            
            print("Verificaciones fallidas:")
            for check, result in results.items():
                if not result:
                    print(f"  - {check}")
            
            return False
    else:
        print_info("ℹ️  Configuración de DESARROLLO")
        print(f"\n{YELLOW}Algunas advertencias son normales en desarrollo{RESET}")
        print(f"{YELLOW}Asegúrate de corregirlas antes de producción{RESET}\n")
        return True

def main():
    """Main function"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}AUDITORÍA DE SEGURIDAD - RICOH FLEET MANAGEMENT{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # Load .env if exists
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Variables cargadas desde {env_path}")
        else:
            print(f"⚠️  Archivo .env no encontrado, usando variables del sistema")
    except ImportError:
        print("⚠️  python-dotenv no instalado, usando variables del sistema")
    
    # Run checks
    results = {
        'ENVIRONMENT': check_environment(),
        'DEBUG': check_debug(),
        'ENCRYPTION_KEY': check_encryption_key(),
        'SECRET_KEY': check_secret_key(),
        'CORS_ORIGINS': check_cors(),
        'Redis': check_redis(),
        'Database': check_database(),
        'Ricoh Password': check_ricoh_password(),
        'HTTPS': check_https(),
        'Log Level': check_log_level()
    }
    
    # Print summary
    success = print_summary(results)
    
    # Exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
