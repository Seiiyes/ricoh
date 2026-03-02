#!/usr/bin/env python3
"""
Probar URL de Contadores Encontrada
URL: /web/entry/es/websys/status/getUnificationCounter.cgi
"""
import requests
import re
import base64
from bs4 import BeautifulSoup
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PRINTER_IP = "192.168.91.251"
ADMIN_USER = "admin"
ADMIN_PASS = ""

print("=" * 80)
print("🔍 PROBANDO URL DE CONTADORES ENCONTRADA")
print("=" * 80)
print(f"\nImpresora: {PRINTER_IP}")
print(f"URL: /web/entry/es/websys/status/getUnificationCounter.cgi")
print()

session = requests.Session()
session.verify = False

# Login
print("1. Login...")
try:
    login_form_url = f"http://{PRINTER_IP}/web/guest/es/websys/webArch/authForm.cgi"
    form_resp = session.get(login_form_url, timeout=10)
    token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
    login_token = token_match.group(1) if token_match else ""
    
    userid_b64 = base64.b64encode(ADMIN_USER.encode()).decode()
    login_url = f"http://{PRINTER_IP}/web/guest/es/websys/webArch/login.cgi"
    login_data = {
        'wimToken': login_token,
        'userid_work': '',
        'userid': userid_b64,
        'password_work': '',
        'password': ADMIN_PASS,
        'open': '',
    }
    
    session.post(login_url, data=login_data, timeout=10, allow_redirects=True)
    print("   ✅ Login OK")
except Exception as e:
    print(f"   ❌ Error en login: {e}")
    exit(1)

# Probar URL de contadores
print("\n2. Accediendo a URL de contadores...")
counter_url = f"http://{PRINTER_IP}/web/entry/es/websys/status/getUnificationCounter.cgi"

try:
    resp = session.get(counter_url, timeout=10)
    print(f"   Status Code: {resp.status_code}")
    print(f"   Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"   Content-Length: {len(resp.text)} bytes")
    
    if resp.status_code == 200:
        print("\n   ✅ URL accesible!")
        
        # Guardar respuesta completa
        with open('contadores_respuesta_completa.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("   💾 Respuesta guardada en: contadores_respuesta_completa.html")
        
        # Analizar contenido
        print("\n3. Analizando contenido...")
        
        # Verificar si es JSON
        if 'json' in resp.headers.get('Content-Type', '').lower():
            print("   📊 Formato: JSON")
            try:
                data = resp.json()
                print(f"   Estructura JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
            except:
                print("   ⚠️  No se pudo parsear como JSON")
        
        # Verificar si es HTML
        elif 'html' in resp.headers.get('Content-Type', '').lower() or '<html' in resp.text.lower():
            print("   📄 Formato: HTML")
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Buscar tablas
            tables = soup.find_all('table')
            print(f"   Tablas encontradas: {len(tables)}")
            
            # Buscar números que parezcan contadores
            numbers = re.findall(r'\b\d{4,8}\b', resp.text)
            if numbers:
                print(f"   📊 Números encontrados (posibles contadores): {numbers[:10]}")
            
            # Buscar palabras clave
            keywords = ['total', 'contador', 'counter', 'páginas', 'pages', 'color', 'blanco', 'negro', 'b/w', 'copia', 'copy', 'impresión', 'print', 'escaneo', 'scan']
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in resp.text.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                print(f"   🔍 Palabras clave encontradas: {', '.join(found_keywords)}")
            
            # Mostrar primeros 500 caracteres del texto visible
            text = soup.get_text()
            clean_text = ' '.join(text.split())[:500]
            print(f"\n   Texto visible (primeros 500 chars):")
            print(f"   {clean_text}")
        
        # Verificar si es XML
        elif 'xml' in resp.headers.get('Content-Type', '').lower() or '<?xml' in resp.text:
            print("   📋 Formato: XML")
            print(f"   Contenido (primeros 1000 chars):")
            print(resp.text[:1000])
        
        # Otro formato
        else:
            print("   ❓ Formato desconocido")
            print(f"   Contenido (primeros 500 chars):")
            print(resp.text[:500])
        
        # Buscar patrones específicos de contadores
        print("\n4. Buscando patrones de contadores...")
        
        # Patrón: nombre=valor
        patterns = [
            (r'total[^=]*=\s*(\d+)', 'Total'),
            (r'color[^=]*=\s*(\d+)', 'Color'),
            (r'black[^=]*=\s*(\d+)', 'Black/White'),
            (r'copy[^=]*=\s*(\d+)', 'Copy'),
            (r'print[^=]*=\s*(\d+)', 'Print'),
            (r'scan[^=]*=\s*(\d+)', 'Scan'),
        ]
        
        for pattern, name in patterns:
            matches = re.findall(pattern, resp.text, re.IGNORECASE)
            if matches:
                print(f"   📊 {name}: {matches}")
        
        # Buscar variables JavaScript
        js_vars = re.findall(r'var\s+(\w+)\s*=\s*["\']?(\d+)["\']?', resp.text)
        if js_vars:
            print(f"\n   Variables JavaScript encontradas:")
            for var_name, value in js_vars[:10]:
                print(f"      {var_name} = {value}")
        
    else:
        print(f"\n   ❌ Error: Status {resp.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ PRUEBA COMPLETADA")
print("=" * 80)
print("\nRevisa el archivo 'contadores_respuesta_completa.html' para ver el contenido completo")
