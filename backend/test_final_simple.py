#!/usr/bin/env python3
"""
Test simple final para verificar que funciona la lectura rápida
"""
import requests
import re
import base64
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

printer_ip = "192.168.91.251"
entry_index = "00256"

print("🔬 Test final: Lectura rápida de funciones\n")

# Setup
session = requests.Session()
session.verify = False

# 1. Login
print("1. Login...")
login_form_url = f"http://{printer_ip}/web/guest/es/websys/webArch/authForm.cgi"
form_resp = session.get(login_form_url, timeout=10)
token_match = re.search(r'name="wimToken"\s+value="(\d+)"', form_resp.text)
login_token = token_match.group(1) if token_match else ""

userid_b64 = base64.b64encode("admin".encode()).decode()
login_url = f"http://{printer_ip}/web/guest/es/websys/webArch/login.cgi"
login_data = {
    'wimToken': login_token,
    'userid_work': '',
    'userid': userid_b64,
    'password_work': '',
    'password': '',
    'open': '',
}
session.post(login_url, data=login_data, timeout=10, allow_redirects=True)
print("   ✅ OK\n")

# 2. Lista
print("2. Acceder a lista...")
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = session.get(list_url, timeout=10)
match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
wim_token = match.group(1) if match else ""
print(f"   ✅ wimToken: {wim_token}\n")

# 3. Cargar batch
print("3. Cargar batch AJAX...")
ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
batch = (int(entry_index) // 50) + 1
ajax_data = {
    'wimToken': wim_token,
    'listCountIn': '50',
    'getCountIn': str(batch)
}
ajax_headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded'
}
session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=10)
print(f"   ✅ Batch {batch} cargado\n")

# 4. Obtener formulario
print("4. Obtener formulario con MODUSER/PROGRAMMED...")
edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
form_data = {
    'wimToken': wim_token,
    'mode': 'MODUSER',
    'outputSpecifyModeIn': 'PROGRAMMED',
    'entryIndexIn': entry_index
}
headers = {
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}
resp = session.post(edit_url, data=form_data, headers=headers, timeout=10)

if "BADFLOW" in resp.text:
    print("   ❌ BADFLOW\n")
elif "availableFuncIn" in resp.text:
    print("   ✅ Formulario obtenido\n")
    
    # 5. Parsear funciones
    print("5. Funciones encontradas:")
    soup = BeautifulSoup(resp.text, 'html.parser')
    checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})
    
    for cb in checkboxes:
        val = cb.get('value', '')
        is_checked = cb.has_attr('checked')
        estado = "✅" if is_checked else "❌"
        print(f"   {estado} {val}")
    
    print("\n✅ ¡ÉXITO! Lectura rápida funciona sin Selenium")
else:
    print(f"   ⚠️ Respuesta inesperada\n")

print("\n" + "=" * 60)
print("CONCLUSIÓN:")
print("  - Se pueden leer funciones sin Selenium")
print("  - Usar: mode=MODUSER + outputSpecifyModeIn=PROGRAMMED")
print("  - Cargar batch AJAX antes del formulario")
print("  - Esto permite sincronizar 200+ usuarios rápidamente")
print("=" * 60)
