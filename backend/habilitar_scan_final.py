#!/usr/bin/env python3
"""
Script final para habilitar SCAN - Usando PROGRAMMED + campos manuales
"""
import requests
import re
import base64
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

printer_ip = "192.168.91.251"
entry_index = "00256"
user_code = "7104"
user_name = "JUAN LIZARAZO"

print("=" * 70)
print(f"HABILITANDO SCAN PARA USUARIO {user_code} - {user_name}")
print("=" * 70)

session = requests.Session()
session.verify = False

# 1. Login
print("\n1. Login...")
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
print("   OK")

# 2. Obtener wimToken
print("\n2. Obtener wimToken...")
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = session.get(list_url, timeout=10)
match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
wim_token = match.group(1) if match else ""
print(f"   wimToken: {wim_token}")

# 3. Cargar batch
print("\n3. Cargar batch...")
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
print(f"   Batch {batch} OK")

# 4. Obtener formulario con PROGRAMMED (trae checkboxes)
print("\n4. Obtener formulario...")
edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"

form_data = {
    'wimToken': wim_token,
    'mode': 'MODUSER',
    'entryIndexIn': entry_index,
    'outputSpecifyModeIn': 'PROGRAMMED',
    'inputSpecifyModeIn': 'READ',
}

headers = {
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}

resp = session.post(edit_url, data=form_data, headers=headers, timeout=10)

if "BADFLOW" in resp.text:
    print("   ERROR: BADFLOW")
    exit(1)

print("   OK")

soup = BeautifulSoup(resp.text, 'html.parser')

# Obtener nuevo wimToken del formulario
token_input = soup.find('input', {'name': 'wimToken'})
if token_input:
    wim_token = token_input.get('value', wim_token)
    print(f"   Nuevo wimToken: {wim_token}")

# 5. Leer funciones actuales
print("\n5. Funciones actuales:")
checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})

if not checkboxes:
    print("   ERROR: No se encontraron checkboxes")
    exit(1)

current_functions = []
for cb in checkboxes:
    val = cb.get('value', '')
    is_checked = cb.has_attr('checked')
    if is_checked:
        current_functions.append(val)
        print(f"   [X] {val}")
    else:
        print(f"   [ ] {val}")

# 6. Agregar SCAN
print("\n6. Habilitar SCAN...")
scan_value = None
for cb in checkboxes:
    val = cb.get('value', '')
    if 'SCAN' in val.upper():
        scan_value = val
        break

if not scan_value:
    print("   ERROR: No se encontro checkbox de SCAN")
    exit(1)

if scan_value not in current_functions:
    current_functions.append(scan_value)
    print(f"   Agregando: {scan_value}")
else:
    print(f"   SCAN ya estaba habilitado")

# 7. Construir payload con TODOS los campos necesarios
print("\n7. Preparar actualizacion...")

# CAMPOS OBLIGATORIOS que Ricoh espera
payload = [
    ('wimToken', wim_token),
    ('mode', 'MODUSER'),
    ('inputSpecifyModeIn', 'WRITE'),
    ('listUpdateIn', 'UPDATE'),
    ('entryIndexIn', entry_index),
    ('entryNameIn', user_name),
    ('entryDisplayNameIn', user_name),
    ('userCodeIn', user_code),
    ('priorityIn', '5'),
    ('outputSpecifyModeIn', ''),
    ('pageSpecifiedIn', ''),
    ('pageNumberIn', ''),
    ('wayFrom', 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
    ('wayTo', 'adrsList.cgi'),
    ('isSelfPasswordEditMode', 'false'),
    ('isLocalAuthPasswordUpdated', 'false'),
    ('isFolderAuthPasswordUpdated', 'false'),
    ('entryTagInfoIn', '1'),
    ('entryTagInfoIn', '1'),
    ('entryTagInfoIn', '1'),
    ('entryTagInfoIn', '1'),
    ('smtpAuthAccountIn', 'AUTH_SYSTEM_O'),
    ('folderAuthAccountIn', 'AUTH_ASSIGNMENT_O'),
    ('folderAuthUserNameIn', ''),
    ('ldapAuthAccountIn', 'AUTH_SYSTEM_O'),
    ('entryUseIn', 'ENTRYUSE_TO_O'),
    ('entryUseIn', 'ENTRYUSE_FROM_O'),
    ('isCertificateExist', 'false'),
    ('isEncryptAlways', 'false'),
    ('folderProtocolIn', 'SMB_O'),
    ('folderPathNameIn', '\\\\TIC-0122\\Escaner'),
]

# Agregar funciones
for func in current_functions:
    payload.append(('availableFuncIn', func))

print(f"   {len(payload)} campos totales")
print(f"   Funciones a habilitar: {len(current_functions)}")
for func in current_functions:
    print(f"      - {func}")

# 8. Enviar actualización
print("\n8. Enviar actualizacion...")
update_url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"
update_headers = {
    'Referer': edit_url,
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded'
}

update_resp = session.post(update_url, data=payload, headers=update_headers, timeout=10)

print(f"   Status: {update_resp.status_code}")

# Guardar respuesta
with open("respuesta_final.html", "w", encoding="utf-8") as f:
    f.write(update_resp.text)

if update_resp.status_code == 200:
    if "BADFLOW" in update_resp.text:
        print("   ERROR: BADFLOW en actualizacion")
    elif "Error" in update_resp.text or "error" in update_resp.text.lower():
        print("   ADVERTENCIA: Posible error")
        print(f"   Revisar: respuesta_final.html")
    else:
        print("   OK: Actualizacion enviada")
        
        # 9. Verificar
        print("\n9. Verificar cambios...")
        
        # Recargar batch
        session.post(ajax_url, data=ajax_data, headers=ajax_headers, timeout=10)
        
        # Leer formulario de nuevo
        verify_resp = session.post(edit_url, data=form_data, headers=headers, timeout=10)
        
        soup = BeautifulSoup(verify_resp.text, 'html.parser')
        checkboxes = soup.find_all('input', {'name': 'availableFuncIn', 'type': 'checkbox'})
        
        scan_enabled = False
        print("   Funciones despues:")
        for cb in checkboxes:
            val = cb.get('value', '')
            is_checked = cb.has_attr('checked')
            if is_checked:
                print(f"   [X] {val}")
                if 'SCAN' in val.upper():
                    scan_enabled = True
            else:
                print(f"   [ ] {val}")
        
        if scan_enabled:
            print(f"\n   EXITO! SCAN habilitado para usuario {user_code}")
        else:
            print(f"\n   SCAN no aparece habilitado")
            print(f"   (Revisar manualmente en la impresora)")
else:
    print(f"   ERROR: Status {update_resp.status_code}")
    print(f"   Revisar: respuesta_final.html")

print("\n" + "=" * 70)
print("PROCESO COMPLETADO")
print("=" * 70)
