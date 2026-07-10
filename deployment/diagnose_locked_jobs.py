#!/usr/bin/env python3
"""
Diagnóstico: inspeccionar lockedPrint.cgi para ver los campos del formulario
de eliminación de trabajos IMPRESIÓN BLOQUEADA en impresoras Ricoh.
"""
import sys
import os
import requests
from bs4 import BeautifulSoup

PRINTER_IP = "192.168.91.251"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "Temporal2021"

BASE_URL = f"http://{PRINTER_IP}"
LOGIN_URL = f"{BASE_URL}/web/entry/es/websys/webArch/authForm.cgi"
LOCKED_URL = f"{BASE_URL}/web/entry/es/webprinter/lockedPrint.cgi"
STORED_URL = f"{BASE_URL}/web/entry/es/webprinter/storedJob.cgi"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

print("=" * 60)
print(f"Conectando a impresora {PRINTER_IP}")
print("=" * 60)

# 1. Login
print("\n[1] Autenticando como admin...")
login_data = {
    'wimUSRID': ADMIN_USER,
    'wimPasswd': ADMIN_PASSWORD,
    'encrypted': '0',
    'wimOKURL': '/web/entry/es/websys/webArch/topPage.cgi',
    'LoginWithCookie': '0',
}
resp = session.post(LOGIN_URL, data=login_data, timeout=15, allow_redirects=True)
print(f"  Login status: {resp.status_code}")

# 2. GET lockedPrint.cgi
print(f"\n[2] Obteniendo lockedPrint.cgi...")
resp = session.get(LOCKED_URL, timeout=15, headers={
    'Referer': f'{BASE_URL}/web/entry/es/websys/webArch/topPage.cgi'
})
print(f"  Status: {resp.status_code}")
soup = BeautifulSoup(resp.text, 'html.parser')

print("\n  --- Campos de formulario en lockedPrint.cgi ---")
for inp in soup.find_all('input'):
    print(f"    [{inp.get('type','text')}] name={inp.get('name','')!r:30s} value={inp.get('value','')!r}")

print("\n  --- Trabajos listados (ID) ---")
job_ids = [el.get('value','') for el in soup.find_all('input', {'name': 'ID'})]
print(f"    Job IDs: {job_ids}")

display_ids = [el.get('value','') for el in soup.find_all('input', {'name': 'display_ID'})]
print(f"    Display IDs: {display_ids}")

wim = soup.find('input', {'name': 'wimToken'})
print(f"    wimToken: {wim.get('value','') if wim else 'NO ENCONTRADO'}")

# Guardar HTML
with open('C:/Users/juan.lizarazo/Desktop/ricoh/locked_page_debug.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print("\n  HTML guardado en: locked_page_debug.html")

# 3. storedJob.cgi para comparar
print(f"\n[3] storedJob.cgi para comparar...")
resp2 = session.get(STORED_URL, timeout=15, headers={
    'Referer': f'{BASE_URL}/web/entry/es/websys/webArch/topPage.cgi'
})
soup2 = BeautifulSoup(resp2.text, 'html.parser')
print("\n  --- Campos en storedJob.cgi ---")
for inp in soup2.find_all('input'):
    print(f"    [{inp.get('type','text')}] name={inp.get('name','')!r:30s} value={inp.get('value','')!r}")
job_ids2 = [el.get('value','') for el in soup2.find_all('input', {'name': 'ID'})]
print(f"    Job IDs en storedJob.cgi: {job_ids2}")

with open('C:/Users/juan.lizarazo/Desktop/ricoh/stored_page_debug.html', 'w', encoding='utf-8') as f:
    f.write(resp2.text)
print("  HTML guardado en: stored_page_debug.html")
print("\n" + "=" * 60)
print("Diagnóstico completado.")
