#!/usr/bin/env python3
"""
Guardar HTML del contador 252 con autenticación correcta
"""
import requests
import base64
from bs4 import BeautifulSoup

PRINTER_IP = "192.168.91.252"

session = requests.Session()
session.verify = False

# Login con método correcto
print("🔐 Haciendo login...")
auth_url = f"http://{PRINTER_IP}/web/guest/es/websys/webArch/authForm.cgi?open=websys/status/getUnificationCounter.cgi"
auth_resp = session.get(auth_url, timeout=10)

soup = BeautifulSoup(auth_resp.text, 'html.parser')
wim_token_input = soup.find('input', {'name': 'wimToken'})
wim_token = wim_token_input.get('value') if wim_token_input else None

login_url = f"http://{PRINTER_IP}/web/guest/es/websys/webArch/login.cgi"

login_data = {
    'userid': base64.b64encode('admin'.encode()).decode(),
    'password': base64.b64encode(''.encode()).decode(),
    'userid_work': '',
    'password_work': ''
}

if wim_token:
    login_data['wimToken'] = wim_token

session.post(login_url, data=login_data, timeout=10)
print("✅ Login completado")

# Obtener contador
print("\n📡 Obteniendo contador...")
counter_url = f"http://{PRINTER_IP}/web/entry/es/websys/status/getUnificationCounter.cgi"
resp = session.get(counter_url, timeout=10)

print(f"Status: {resp.status_code}")
print(f"Content-Length: {len(resp.content)} bytes")

# Guardar
with open("contador_252_autenticado.html", "w", encoding="utf-8") as f:
    f.write(resp.text)

print(f"\n💾 HTML guardado en: contador_252_autenticado.html")
print(f"📊 Tamaño: {len(resp.content)} bytes")

# Analizar rápidamente
soup = BeautifulSoup(resp.text, 'html.parser')
tables = soup.find_all('table')
print(f"📋 Tablas encontradas: {len(tables)}")

# Buscar "Copiadora" e "Impresora"
if "Copiadora" in resp.text:
    print("✅ Contiene 'Copiadora'")
else:
    print("❌ NO contiene 'Copiadora'")

if "Impresora" in resp.text:
    print("✅ Contiene 'Impresora'")
else:
    print("❌ NO contiene 'Impresora'")
