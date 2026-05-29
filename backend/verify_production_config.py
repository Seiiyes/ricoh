#!/usr/bin/env python3
"""
Production Configuration Verification Script
Verifica que la configuración de producción esté correcta antes del despliegue
"""
import os
import sys
from pathlib import Path

# Colors for terminal output
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

def check_env_file():
    """Check if .env file exists"""
    print_header("1. Verificando archivo .env")
    
    env_path = Path(".env")
    if not env_path.exists():
        print_error("Archivo .env NO existe")
        print(f"   Crear desde: cp .env.production.example .env")
        return False
    
    print_success("Archivo .env existe")
    return True

def check_critical_vars():
    """Check critical environment variables"""
    print_header("2. Verificando variables críticas")
    
    # Load .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print_warning("python-dotenv no instalado, usando variables del sistema")
    
    critical_vars = {
        'DATABASE_URL': 'URL de conexión a PostgreSQL',
        'REDIS_URL': 'URL de conexión a Redis',
        'ENCRYPTION_KEY': 'Clave de encriptación',
        'SECRET_KEY': 'Clave secreta para JWT',
        'RICOH_ADMIN_PASSWORD': 'Contraseña admin de impresoras'
    }
    
    all_ok = True
    for var, description in critical_vars.items():
        value = os.getenv(var)
        if not value:
            print_error(f"{var} NO configurada ({description})")
            all_ok = False
        elif value in ['your-encryption-key-here', 'your-secret-key-here', 'CHANGE_THIS', 'GENERATE_NEW']:
            print_error(f"{var} tiene valor de ejemplo, debe cambiarse")
            all_ok = False
        else:
            # Mask sensitive values
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print_success(f"{var} = {masked}")
    
    return all_ok

def check_environment_setting():
    """Check ENVIRONMENT variable"""
    print_header("3. Verificando configuración de ambiente")
    
    env = os.getenv('ENVIRONMENT', 'development')
    debug = os.getenv('DEBUG', 'true').lower()
    
    if env != 'production':
        print_error(f"ENVIRONMENT = {env} (debe ser 'production')")
        return False
    
    print_success(f"ENVIRONMENT = {env}")
    
    if debug == 'true':
        print_error(f"DEBUG = {debug} (debe ser 'false' en producción)")
        return False
    
    print_success(f"DEBUG = {debug}")
    return True

def check_redis_connection():
    """Check Redis connection"""
    print_header("4. Verificando conexión a Redis")
    
    try:
        import redis
        
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print_error("REDIS_URL no configurada")
            return False
        
        # Parse URL to show connection details
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        print(f"   Conectando a: {parsed.hostname}:{parsed.port or 6379}")
        
        # Try to connect
        client = redis.from_url(redis_url, socket_connect_timeout=5)
        response = client.ping()
        
        if response:
            print_success("Redis conectado correctamente")
            
            # Get info
            info = client.info()
            print(f"   Versión: {info.get('redis_version', 'N/A')}")
            print(f"   Memoria: {info.get('used_memory_human', 'N/A')}")
            print(f"   Keys: {client.dbsize()}")
            return True
        else:
            print_error("Redis no responde")
            return False
            
    except ImportError:
        print_error("Módulo 'redis' no instalado")
        print("   Instalar: pip install redis hiredis")
        return False
    except Exception as e:
        print_error(f"Error conectando a Redis: {e}")
        return False

def check_database_connection():
    """Check database connection"""
    print_header("5. Verificando conexión a PostgreSQL")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            print_error("DATABASE_URL no configurada")
            return False
        
        # Parse URL
        parsed = urlparse(db_url)
        print(f"   Conectando a: {parsed.hostname}:{parsed.port or 5432}/{parsed.path[1:]}")
        
        # Try to connect
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print_success("PostgreSQL conectado correctamente")
        print(f"   {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print_error("Módulo 'psycopg2' no instalado")
        print("   Instalar: pip install psycopg2-binary")
        return False
    except Exception as e:
        print_error(f"Error conectando a PostgreSQL: {e}")
        return False

def check_cors_configuration():
    """Check CORS configuration"""
    print_header("6. Verificando configuración CORS")
    
    cors_origins = os.getenv('CORS_ORIGINS', '')
    
    if not cors_origins:
        print_error("CORS_ORIGINS no configurada")
        return False
    
    if 'localhost' in cors_origins or '127.0.0.1' in cors_origins:
        print_warning("CORS_ORIGINS contiene localhost (no recomendado en producción)")
        print(f"   Actual: {cors_origins}")
        return False
    
    origins = [o.strip() for o in cors_origins.split(',')]
    print_success(f"CORS configurado para {len(origins)} dominio(s):")
    for origin in origins:
        print(f"   - {origin}")
    
    return True

def check_security_settings():
    """Check security settings"""
    print_header("7. Verificando configuración de seguridad")
    
    checks = []
    
    # Check ENCRYPTION_KEY length
    encryption_key = os.getenv('ENCRYPTION_KEY', '')
    if len(encryption_key) >= 32:
        print_success(f"ENCRYPTION_KEY tiene longitud adecuada ({len(encryption_key)} chars)")
        checks.append(True)
    else:
        print_error(f"ENCRYPTION_KEY muy corta ({len(encryption_key)} chars, mínimo 32)")
        checks.append(False)
    
    # Check SECRET_KEY length
    secret_key = os.getenv('SECRET_KEY', '')
    if len(secret_key) >= 32:
        print_success(f"SECRET_KEY tiene longitud adecuada ({len(secret_key)} chars)")
        checks.append(True)
    else:
        print_error(f"SECRET_KEY muy corta ({len(secret_key)} chars, mínimo 32)")
        checks.append(False)
    
    # Check RICOH_ADMIN_PASSWORD
    ricoh_pass = os.getenv('RICOH_ADMIN_PASSWORD', '')
    if len(ricoh_pass) >= 8:
        print_success(f"RICOH_ADMIN_PASSWORD configurada")
        checks.append(True)
    else:
        print_error("RICOH_ADMIN_PASSWORD no configurada o muy corta")
        checks.append(False)
    
    return all(checks)

def check_cache_configuration():
    """Check cache TTL configuration"""
    print_header("8. Verificando configuración de caché")
    
    ttl_dashboard = os.getenv('CACHE_TTL_DASHBOARD', '300')
    ttl_analytics = os.getenv('CACHE_TTL_ANALYTICS', '3600')
    
    print_success(f"CACHE_TTL_DASHBOARD = {ttl_dashboard}s ({int(ttl_dashboard)//60} min)")
    print_success(f"CACHE_TTL_ANALYTICS = {ttl_analytics}s ({int(ttl_analytics)//60} min)")
    
    return True

def check_redis_service():
    """Check RedisService implementation"""
    print_header("9. Verificando RedisService")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from services.redis_service import redis_service, check_redis_health
        
        print_success("RedisService importado correctamente")
        
        # Check if enabled
        if redis_service.is_enabled():
            print_success("Redis HABILITADO")
        else:
            print_warning("Redis DESHABILITADO (usando memoria)")
        
        # Get stats
        stats = check_redis_health()
        print(f"\n   Estadísticas:")
        for key, value in stats.items():
            print(f"   - {key}: {value}")
        
        return redis_service.is_enabled()
        
    except Exception as e:
        print_error(f"Error verificando RedisService: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(results):
    """Print summary and recommendations"""
    print_header("RESUMEN DE VERIFICACIÓN")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"Total de verificaciones: {total}")
    print(f"Exitosas: {GREEN}{passed}{RESET}")
    print(f"Fallidas: {RED}{total - passed}{RESET}")
    print(f"Porcentaje: {(passed/total*100):.1f}%\n")
    
    if passed == total:
        print_success("✅ TODAS LAS VERIFICACIONES PASARON")
        print(f"\n{GREEN}El sistema está listo para producción{RESET}\n")
        return True
    else:
        print_error("❌ ALGUNAS VERIFICACIONES FALLARON")
        print(f"\n{RED}Corregir los errores antes de desplegar{RESET}\n")
        
        print("Verificaciones fallidas:")
        for check, result in results.items():
            if not result:
                print(f"  - {check}")
        
        return False

def main():
    """Main function"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}VERIFICACIÓN DE CONFIGURACIÓN DE PRODUCCIÓN{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # Change to backend directory if needed
    if Path('backend').exists():
        os.chdir('backend')
    
    # Run checks
    results = {
        'Archivo .env': check_env_file(),
        'Variables críticas': check_critical_vars(),
        'Configuración de ambiente': check_environment_setting(),
        'Conexión Redis': check_redis_connection(),
        'Conexión PostgreSQL': check_database_connection(),
        'Configuración CORS': check_cors_configuration(),
        'Configuración de seguridad': check_security_settings(),
        'Configuración de caché': check_cache_configuration(),
        'RedisService': check_redis_service()
    }
    
    # Print summary
    success = print_summary(results)
    
    # Exit code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
