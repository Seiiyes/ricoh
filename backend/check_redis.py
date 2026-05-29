#!/usr/bin/env python3
"""
Redis Configuration Checker
Verifica el estado de Redis y la configuración del sistema
"""
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def check_redis_module():
    """Check if redis module is installed"""
    print("\n" + "="*70)
    print("1. Verificando módulo Python 'redis'")
    print("="*70)
    
    try:
        import redis
        print(f"✅ Módulo 'redis' instalado: versión {redis.__version__}")
        return True
    except ImportError:
        print("❌ Módulo 'redis' NO instalado")
        print("\n   Para instalar:")
        print("   pip install redis==5.0.1 hiredis==2.3.2")
        return False


def check_redis_server():
    """Check if Redis server is running"""
    print("\n" + "="*70)
    print("2. Verificando servidor Redis")
    print("="*70)
    
    try:
        import redis
        
        # Try to connect
        host = os.getenv("REDIS_HOST", "localhost")
        port = int(os.getenv("REDIS_PORT", 6379))
        
        print(f"   Intentando conectar a {host}:{port}...")
        
        client = redis.Redis(
            host=host,
            port=port,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        
        # Test connection
        response = client.ping()
        
        if response:
            print(f"✅ Servidor Redis ACTIVO en {host}:{port}")
            
            # Get server info
            info = client.info()
            print(f"\n   Información del servidor:")
            print(f"   - Versión: {info.get('redis_version', 'N/A')}")
            print(f"   - Uptime: {info.get('uptime_in_seconds', 0)} segundos")
            print(f"   - Memoria usada: {info.get('used_memory_human', 'N/A')}")
            print(f"   - Clientes conectados: {info.get('connected_clients', 0)}")
            print(f"   - Total de keys: {client.dbsize()}")
            
            return True
        else:
            print(f"❌ Servidor Redis NO responde en {host}:{port}")
            return False
            
    except ImportError:
        print("⚠️  No se puede verificar (módulo 'redis' no instalado)")
        return False
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        print("\n   Posibles causas:")
        print("   - Redis no está instalado")
        print("   - Redis no está corriendo")
        print("   - Puerto 6379 bloqueado")
        print("\n   Para instalar Redis:")
        print("   - Docker: docker run -d --name redis -p 6379:6379 redis:7-alpine")
        print("   - WSL2: sudo apt install redis-server && sudo service redis-server start")
        print("   - Windows: https://github.com/microsoftarchive/redis/releases")
        return False


def check_env_file():
    """Check if .env file exists and has Redis config"""
    print("\n" + "="*70)
    print("3. Verificando archivo .env")
    print("="*70)
    
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if not env_path.exists():
        print("❌ Archivo .env NO existe")
        print(f"\n   Crear desde ejemplo:")
        print(f"   cp {env_example_path} {env_path}")
        return False
    
    print(f"✅ Archivo .env existe: {env_path}")
    
    # Check Redis variables
    redis_vars = [
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_DB",
        "REDIS_URL",
        "CACHE_TTL_DASHBOARD",
        "CACHE_TTL_ANALYTICS"
    ]
    
    print("\n   Variables de Redis:")
    found_vars = []
    
    with open(env_path, 'r') as f:
        content = f.read()
        for var in redis_vars:
            if var in content and not content.split(var)[1].split('\n')[0].strip().startswith('#'):
                value = os.getenv(var, "no configurado")
                print(f"   ✅ {var}={value}")
                found_vars.append(var)
            else:
                print(f"   ⚠️  {var} no configurado")
    
    return len(found_vars) > 0


def check_redis_service():
    """Check RedisService implementation"""
    print("\n" + "="*70)
    print("4. Verificando RedisService")
    print("="*70)
    
    try:
        from services.redis_service import redis_service
        
        print("✅ RedisService importado correctamente")
        
        # Check if enabled
        if redis_service.enabled:
            print("✅ Redis HABILITADO y funcionando")
        else:
            print("⚠️  Redis DESHABILITADO - usando caché en memoria")
            print("   (Esto es normal si Redis no está instalado)")
        
        # Try to get stats
        stats = redis_service.get_stats() if hasattr(redis_service, 'get_stats') else {}
        
        if stats:
            print(f"\n   Estadísticas:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando RedisService: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_api_endpoints():
    """Check if API endpoints use caching"""
    print("\n" + "="*70)
    print("5. Verificando endpoints con caché")
    print("="*70)
    
    endpoints_with_cache = [
        ("backend/api/dashboard.py", ["get_dashboard_kpis", "get_top_impresoras", "get_top_usuarios_consumo", "get_actividad_reciente"]),
        ("backend/api/analytics.py", ["get_evolution", "get_comparison"])
    ]
    
    for file_path, functions in endpoints_with_cache:
        full_path = Path(__file__).parent.parent / file_path
        
        if not full_path.exists():
            print(f"⚠️  {file_path} no encontrado")
            continue
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        print(f"\n   {file_path}:")
        for func in functions:
            if f"def {func}" in content and "@cache_result" in content:
                print(f"   ✅ {func}() usa @cache_result")
            else:
                print(f"   ⚠️  {func}() NO usa caché")


def print_summary(results):
    """Print summary and recommendations"""
    print("\n" + "="*70)
    print("RESUMEN Y RECOMENDACIONES")
    print("="*70)
    
    module_ok, server_ok, env_ok, service_ok = results
    
    if all(results):
        print("\n✅ TODO CONFIGURADO CORRECTAMENTE")
        print("   Redis está operativo y listo para usar")
        return
    
    print("\n⚠️  CONFIGURACIÓN INCOMPLETA\n")
    
    if not module_ok:
        print("📦 PASO 1: Instalar módulo Python")
        print("   cd backend")
        print("   pip install redis==5.0.1 hiredis==2.3.2")
        print()
    
    if not server_ok:
        print("🔧 PASO 2: Instalar y ejecutar Redis")
        print("   Opción A - Docker (más fácil):")
        print("   docker run -d --name redis -p 6379:6379 redis:7-alpine")
        print()
        print("   Opción B - WSL2:")
        print("   sudo apt update && sudo apt install redis-server")
        print("   sudo service redis-server start")
        print()
        print("   Opción C - Windows nativo:")
        print("   https://github.com/microsoftarchive/redis/releases")
        print()
    
    if not env_ok:
        print("⚙️  PASO 3: Configurar .env")
        print("   cp backend/.env.example backend/.env")
        print("   # Editar backend/.env y descomentar/configurar:")
        print("   REDIS_HOST=localhost")
        print("   REDIS_PORT=6379")
        print("   REDIS_URL=redis://localhost:6379/0")
        print()
    
    print("🔄 PASO 4: Reiniciar backend")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    print()
    
    print("💡 ALTERNATIVA: Usar fallback a memoria (solo desarrollo)")
    print("   Si no necesitas Redis en desarrollo, el sistema usará")
    print("   caché en memoria automáticamente.")
    print("   ⚠️  NO recomendado para producción")


def main():
    """Main function"""
    print("\n" + "="*70)
    print("DIAGNÓSTICO DE CONFIGURACIÓN DE REDIS")
    print("="*70)
    
    # Load .env if exists
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✅ Variables de entorno cargadas desde {env_path}")
    except ImportError:
        print("⚠️  python-dotenv no instalado, usando variables de sistema")
    
    # Run checks
    results = (
        check_redis_module(),
        check_redis_server(),
        check_env_file(),
        check_redis_service()
    )
    
    check_api_endpoints()
    
    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
