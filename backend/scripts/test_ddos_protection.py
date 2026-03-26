#!/usr/bin/env python3
"""
Script para probar la protección DDoS
Simula diferentes tipos de ataques para verificar que la protección funciona
"""
import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración
BASE_URL = "http://localhost:8000"
SUPERADMIN_TOKEN = None  # Se obtiene del login


def login_superadmin():
    """Login como superadmin para obtener token"""
    global SUPERADMIN_TOKEN
    
    print("🔐 Iniciando sesión como superadmin...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "superadmin",
            "password": "{:Z75M!=x>9PiPp2"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        SUPERADMIN_TOKEN = data["access_token"]
        print("✅ Login exitoso")
        return True
    else:
        print(f"❌ Login fallido: {response.status_code}")
        return False


def test_normal_traffic():
    """Test 1: Tráfico normal (debería funcionar)"""
    print("\n" + "="*80)
    print("TEST 1: Tráfico Normal")
    print("="*80)
    
    success_count = 0
    for i in range(10):
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            success_count += 1
        
        # Mostrar headers de rate limit
        if i == 0:
            print(f"X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit')}")
            print(f"X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining')}")
        
        time.sleep(0.5)  # Esperar entre requests
    
    print(f"✅ Requests exitosos: {success_count}/10")


def test_rate_limiting():
    """Test 2: Exceder rate limit global"""
    print("\n" + "="*80)
    print("TEST 2: Rate Limiting Global")
    print("="*80)
    
    print("Enviando 110 requests rápidos (límite: 100/min)...")
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(110):
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            rate_limited_count += 1
            if rate_limited_count == 1:
                print(f"⚠️ Rate limit alcanzado en request #{i+1}")
                print(f"Respuesta: {response.json()}")
    
    print(f"✅ Requests exitosos: {success_count}")
    print(f"⚠️ Requests bloqueados por rate limit: {rate_limited_count}")


def test_burst_attack():
    """Test 3: Burst attack (debería bloquear IP)"""
    print("\n" + "="*80)
    print("TEST 3: Burst Attack Detection")
    print("="*80)
    
    print("Enviando 35 requests simultáneos (threshold: 30 en 10s)...")
    
    def make_request(i):
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            return (i, response.status_code)
        except Exception as e:
            return (i, f"Error: {e}")
    
    with ThreadPoolExecutor(max_workers=35) as executor:
        futures = [executor.submit(make_request, i) for i in range(35)]
        
        results = {}
        for future in as_completed(futures):
            i, status = future.result()
            results[i] = status
    
    # Contar resultados
    success = sum(1 for s in results.values() if s == 200)
    blocked = sum(1 for s in results.values() if s == 429)
    forbidden = sum(1 for s in results.values() if s == 403)
    
    print(f"✅ Requests exitosos: {success}")
    print(f"⚠️ Rate limited (429): {blocked}")
    print(f"🚫 IP bloqueada (403): {forbidden}")
    
    # Verificar si IP fue bloqueada
    time.sleep(1)
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 403:
        print("🚫 IP bloqueada exitosamente por burst attack")
        return True
    else:
        print("⚠️ IP no fue bloqueada (puede ser por whitelist)")
        return False


def test_endpoint_rate_limit():
    """Test 4: Rate limit específico de endpoint"""
    print("\n" + "="*80)
    print("TEST 4: Endpoint Rate Limiting")
    print("="*80)
    
    print("Enviando 10 requests a /auth/login (límite: 5/min)...")
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(10):
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "test", "password": "test"}
        )
        
        if response.status_code in [200, 401]:  # 401 es esperado (credenciales inválidas)
            success_count += 1
        elif response.status_code == 429:
            rate_limited_count += 1
            if rate_limited_count == 1:
                print(f"⚠️ Rate limit de endpoint alcanzado en request #{i+1}")
    
    print(f"✅ Requests procesados: {success_count}")
    print(f"⚠️ Requests bloqueados: {rate_limited_count}")


def test_admin_api():
    """Test 5: API de administración"""
    print("\n" + "="*80)
    print("TEST 5: API de Administración DDoS")
    print("="*80)
    
    if not SUPERADMIN_TOKEN:
        print("❌ No hay token de superadmin, saltando test")
        return
    
    headers = {"Authorization": f"Bearer {SUPERADMIN_TOKEN}"}
    
    # Obtener estadísticas
    print("📊 Obteniendo estadísticas...")
    response = requests.get(f"{BASE_URL}/admin/ddos/stats", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ IPs bloqueadas: {stats['blocked_count']}")
        print(f"   Configuración: {stats['config']}")
    else:
        print(f"❌ Error obteniendo stats: {response.status_code}")
    
    # Obtener IPs bloqueadas
    print("\n🚫 Obteniendo IPs bloqueadas...")
    response = requests.get(f"{BASE_URL}/admin/ddos/blocked-ips", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ IPs bloqueadas: {data['count']}")
        if data['blocked_ips']:
            for ip, until in data['blocked_ips'].items():
                print(f"   - {ip} hasta {until}")
    else:
        print(f"❌ Error obteniendo IPs: {response.status_code}")
    
    # Obtener configuración
    print("\n⚙️ Obteniendo configuración...")
    response = requests.get(f"{BASE_URL}/admin/ddos/config", headers=headers)
    if response.status_code == 200:
        config = response.json()
        print(f"✅ Rate limit global: {config['global_rate_limit']}/{config['global_rate_window']}s")
        print(f"   Burst threshold: {config['burst_threshold']} en {config['burst_window']}s")
        print(f"   Duración de bloqueo: {config['block_duration']}s")
    else:
        print(f"❌ Error obteniendo config: {response.status_code}")


def test_payload_size():
    """Test 6: Validación de tamaño de payload"""
    print("\n" + "="*80)
    print("TEST 6: Validación de Tamaño de Payload")
    print("="*80)
    
    print("Enviando payload de 11 MB (límite: 10 MB)...")
    
    # Crear payload grande
    large_data = "x" * (11 * 1024 * 1024)  # 11 MB
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "test", "password": large_data},
            timeout=10
        )
        
        if response.status_code == 413:
            print("✅ Payload rechazado correctamente (413)")
        elif response.status_code == 422:
            print("⚠️ Payload rechazado por validación (422)")
        else:
            print(f"❌ Respuesta inesperada: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error en request: {e}")


def unblock_ip_if_needed():
    """Desbloquear IP si fue bloqueada durante los tests"""
    if not SUPERADMIN_TOKEN:
        return
    
    print("\n" + "="*80)
    print("LIMPIEZA: Desbloqueando IP si es necesario")
    print("="*80)
    
    headers = {"Authorization": f"Bearer {SUPERADMIN_TOKEN}"}
    
    # Obtener IPs bloqueadas
    response = requests.get(f"{BASE_URL}/admin/ddos/blocked-ips", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['blocked_ips']:
            for ip in data['blocked_ips'].keys():
                print(f"🔓 Desbloqueando {ip}...")
                unblock_response = requests.post(
                    f"{BASE_URL}/admin/ddos/unblock-ip",
                    headers=headers,
                    json={"ip": ip}
                )
                if unblock_response.status_code == 200:
                    print(f"✅ {ip} desbloqueada")
                else:
                    print(f"❌ Error desbloqueando {ip}")


def main():
    """Ejecutar todos los tests"""
    print("="*80)
    print("🛡️  PRUEBAS DE PROTECCIÓN DDOS")
    print("="*80)
    print(f"URL Base: {BASE_URL}")
    print()
    
    # Verificar que el servidor está corriendo
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Servidor accesible")
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("Asegúrate de que el servidor está corriendo en http://localhost:8000")
        sys.exit(1)
    
    # Login como superadmin
    if not login_superadmin():
        print("⚠️ No se pudo hacer login, algunos tests se saltarán")
    
    # Ejecutar tests
    try:
        test_normal_traffic()
        time.sleep(2)
        
        test_rate_limiting()
        time.sleep(5)  # Esperar a que expire la ventana
        
        test_endpoint_rate_limit()
        time.sleep(5)
        
        test_payload_size()
        time.sleep(2)
        
        # Test de burst (puede bloquear la IP)
        # test_burst_attack()
        # time.sleep(2)
        
        test_admin_api()
        
        # Limpiar
        unblock_ip_if_needed()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrumpidos por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante los tests: {e}")
    
    print("\n" + "="*80)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*80)


if __name__ == "__main__":
    main()
