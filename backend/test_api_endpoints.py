#!/usr/bin/env python3
"""
Test rápido de endpoints de la API de contadores
Requiere que el servidor esté corriendo en http://localhost:8000
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
PRINTER_ID = 4  # Impresora de prueba

def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)

def test_get_latest_counter():
    """Test: Obtener último contador total"""
    print_section("TEST 1: Obtener Último Contador Total")
    
    url = f"{BASE_URL}/api/counters/printer/{PRINTER_ID}"
    print(f"GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total páginas: {data['total']:,}")
            print(f"   Copiadora B/N: {data['copiadora_bn']:,}")
            print(f"   Impresora B/N: {data['impresora_bn']:,}")
            print(f"   Fecha lectura: {data['fecha_lectura']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("   ⚠️  Asegúrate de que el servidor esté corriendo:")
        print("   cd backend && venv\\Scripts\\python.exe main.py")

def test_get_user_counters():
    """Test: Obtener contadores por usuario"""
    print_section("TEST 2: Obtener Contadores por Usuario")
    
    url = f"{BASE_URL}/api/counters/users/{PRINTER_ID}"
    print(f"GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total usuarios: {len(data)}")
            
            if data:
                # Mostrar top 3
                sorted_users = sorted(data, key=lambda x: x['total_paginas'], reverse=True)
                print("\n📊 Top 3 usuarios:")
                for i, user in enumerate(sorted_users[:3], 1):
                    print(f"   {i}. {user['nombre_usuario']} ({user['codigo_usuario']}): {user['total_paginas']:,} páginas")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_get_history():
    """Test: Obtener histórico de contadores"""
    print_section("TEST 3: Obtener Histórico de Contadores")
    
    url = f"{BASE_URL}/api/counters/printer/{PRINTER_ID}/history?limit=5"
    print(f"GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registros obtenidos: {len(data)}")
            
            if data:
                print("\n📋 Últimos registros:")
                for record in data:
                    fecha = datetime.fromisoformat(record['fecha_lectura'].replace('Z', '+00:00'))
                    print(f"   - {fecha.strftime('%Y-%m-%d %H:%M:%S')}: {record['total']:,} páginas")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_read_counter():
    """Test: Ejecutar lectura manual"""
    print_section("TEST 4: Ejecutar Lectura Manual")
    
    url = f"{BASE_URL}/api/counters/read/{PRINTER_ID}"
    print(f"POST {url}")
    print("⚠️  Esta operación puede tomar 5-10 segundos...")
    
    try:
        response = requests.post(url, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ Lectura exitosa")
                print(f"   Total páginas: {data['contador_total']['total']:,}")
                print(f"   Usuarios guardados: {data['usuarios_count']}")
            else:
                print(f"❌ Error: {data['error']}")
        else:
            print(f"❌ Error: {response.text}")
    except requests.Timeout:
        print("❌ Timeout: La operación tardó demasiado")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_monthly_closes():
    """Test: Obtener cierres mensuales"""
    print_section("TEST 5: Obtener Cierres Mensuales")
    
    url = f"{BASE_URL}/api/counters/monthly/{PRINTER_ID}"
    print(f"GET {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cierres encontrados: {len(data)}")
            
            if data:
                print("\n📅 Cierres mensuales:")
                for cierre in data:
                    print(f"   - {cierre['anio']}-{cierre['mes']:02d}: {cierre['total_paginas']:,} páginas (Δ {cierre['diferencia_total']:,})")
            else:
                print("   ℹ️  No hay cierres mensuales registrados")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_api_root():
    """Test: Verificar que el servidor esté corriendo"""
    print_section("TEST 0: Verificar Servidor")
    
    url = f"{BASE_URL}/"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Servidor online")
            print(f"   Servicio: {data['service']}")
            print(f"   Versión: {data['version']}")
            print(f"   Base de datos: {data['database']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        print("\n⚠️  Para iniciar el servidor:")
        print("   cd backend")
        print("   venv\\Scripts\\python.exe main.py")
        print("   O ejecutar: start-api-server.bat")
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 80)
    print("🧪 TEST DE ENDPOINTS DE LA API DE CONTADORES")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Impresora de prueba: ID {PRINTER_ID}")
    
    # Verificar que el servidor esté corriendo
    if not test_api_root():
        return
    
    # Ejecutar tests
    test_get_latest_counter()
    test_get_user_counters()
    test_get_history()
    test_monthly_closes()
    
    # Test de lectura manual (comentado por defecto porque tarda)
    print("\n" + "=" * 80)
    print("ℹ️  TEST 4 (Lectura Manual) omitido por defecto")
    print("   Para ejecutarlo, descomenta la línea en el código")
    print("=" * 80)
    # test_read_counter()  # Descomentar para probar lectura manual
    
    print("\n" + "=" * 80)
    print("✅ TESTS COMPLETADOS")
    print("=" * 80)
    print("\n💡 Para ver la documentación interactiva:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   ReDoc: http://localhost:8000/redoc")
    print()

if __name__ == "__main__":
    main()
