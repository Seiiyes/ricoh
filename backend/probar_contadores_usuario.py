#!/usr/bin/env python3
"""
Probar URL de Contadores por Usuario
URL: /web/entry/es/websys/status/getUserCounter.cgi
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
print("🔍 PROBANDO URL DE CONTADORES POR USUARIO")
print("=" * 80)
print(f"\nImpresora: {PRINTER_IP}")
print(f"URL: /web/entry/es/websys/status/getUserCounter.cgi")
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

# Probar URL de contadores por usuario
print("\n2. Accediendo a URL de contadores por usuario...")
counter_url = f"http://{PRINTER_IP}/web/entry/es/websys/status/getUserCounter.cgi"

try:
    resp = session.get(counter_url, timeout=10)
    print(f"   Status Code: {resp.status_code}")
    print(f"   Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
    print(f"   Content-Length: {len(resp.text)} bytes")
    
    if resp.status_code == 200:
        print("\n   ✅ URL accesible!")
        
        # Guardar respuesta completa
        with open('contadores_usuario_respuesta.html', 'w', encoding='utf-8') as f:
            f.write(resp.text)
        print("   💾 Respuesta guardada en: contadores_usuario_respuesta.html")
        
        # Analizar contenido
        print("\n3. Analizando contenido...")
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Buscar tablas
        tables = soup.find_all('table')
        print(f"   Tablas encontradas: {len(tables)}")
        
        # Buscar filas de usuarios
        rows = soup.find_all('tr')
        print(f"   Filas encontradas: {len(rows)}")
        
        # Buscar palabras clave
        keywords = ['usuario', 'user', 'nombre', 'name', 'código', 'code', 'total', 'páginas', 'pages', 'color', 'blanco', 'negro', 'copia', 'copy', 'impresión', 'print', 'escaneo', 'scan']
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in resp.text.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"   🔍 Palabras clave encontradas: {', '.join(found_keywords)}")
        
        # Mostrar primeros 1000 caracteres del texto visible
        text = soup.get_text()
        clean_text = ' '.join(text.split())[:1000]
        print(f"\n   Texto visible (primeros 1000 chars):")
        print(f"   {clean_text}")
        
        # Buscar números que parezcan contadores
        numbers = re.findall(r'\b\d{2,8}\b', resp.text)
        if numbers:
            print(f"\n   📊 Números encontrados (posibles contadores): {numbers[:20]}")
        
        # Intentar identificar estructura de tabla
        print("\n4. Analizando estructura de tabla...")
        
        # Buscar encabezados de tabla
        headers = []
        for table in tables:
            header_row = table.find('tr')
            if header_row:
                cells = header_row.find_all(['th', 'td'])
                if cells:
                    row_headers = [cell.get_text(strip=True) for cell in cells]
                    if row_headers and any(row_headers):
                        headers.append(row_headers)
        
        if headers:
            print(f"   📋 Encabezados de tabla encontrados:")
            for i, header in enumerate(headers[:3]):
                print(f"      Tabla {i+1}: {header}")
        
        # Buscar filas de datos
        print("\n5. Buscando datos de usuarios...")
        user_rows = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all('td')
                if len(cells) >= 3:  # Al menos 3 columnas
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    # Verificar si parece una fila de usuario (tiene nombre y números)
                    has_text = any(cell for cell in row_data if cell and not cell.isdigit())
                    has_numbers = any(cell for cell in row_data if cell.isdigit())
                    if has_text and has_numbers:
                        user_rows.append(row_data)
        
        if user_rows:
            print(f"   ✅ Encontradas {len(user_rows)} filas de usuarios")
            print(f"\n   Primeras 5 filas:")
            for i, row in enumerate(user_rows[:5]):
                print(f"      {i+1}. {row}")
        else:
            print(f"   ⚠️  No se encontraron filas de usuarios")
        
    else:
        print(f"\n   ❌ Error: Status {resp.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ PRUEBA COMPLETADA")
print("=" * 80)
print("\nRevisa el archivo 'contadores_usuario_respuesta.html' para ver el contenido completo")
