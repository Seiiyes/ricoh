"""
Test user provisioning and deletion on printer 192.168.91.253 (which uses adrsDeleteEntry.cgi).
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

import re
from services.ricoh_web_client import get_ricoh_web_client
from db.database import SessionLocal
from db.repository import PrinterRepository

printer_ip = "192.168.91.253"

db = SessionLocal()
printer = PrinterRepository.get_by_ip(db, printer_ip)
admin_password = printer.admin_password if printer else None
db.close()

client = get_ricoh_web_client()
client.reset_session()

# Step 1: Provision a dummy user
user_config = {
    'nombre': 'TEST_DELETE_253',
    'codigo_de_usuario': '9999',
    'contrasena_inicio_sesion': 'Temporal2021',
    'funciones_disponibles': {
        'copiadora': False,
        'copiadora_color': False,
        'impresora': False,
        'impresora_color': False,
        'escaner': False,
        'document_server': False,
        'fax': False,
        'navegador': False
    }
}

print("Creating dummy user on .253...")
provision_res = client.provision_user(printer_ip, user_config, admin_password=admin_password, logout=False)
print(f"Provision result: {provision_res}")

if not provision_res or not isinstance(provision_res, tuple):
    print("Failed to provision dummy user")
    sys.exit(1)

success, entry_index = provision_res
print(f"Dummy user created at entry_index={entry_index}")

# Step 2: Delete the dummy user using adrsDeleteEntry.cgi
print("\nProceeding to delete dummy user...")
# Get fresh wimToken
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = client.session.get(list_url, timeout=30)
wim_token = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text).group(1)
print(f"wimToken: {wim_token}")

delete_url = f"http://{printer_ip}/web/entry/es/address/adrsDeleteEntry.cgi"
payload = {
    'wimToken': wim_token,
    'entryIndexIn': entry_index,
    'inputSpecifyModeIn': 'WRITE',
    'listUpdateIn': 'UPDATE',
    'mode': 'DELETE',
    'wayFrom': 'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS',
    'wayTo': 'adrsList.cgi'
}
headers = {
    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsConfirmDelete.cgi", # Referer is important
    'Content-Type': 'application/x-www-form-urlencoded'
}

print(f"Sending delete POST to {delete_url} with payload {payload}")
resp = client.session.post(delete_url, data=payload, headers=headers, timeout=30)
print(f"Delete response status: {resp.status_code}")
print(f"Delete response length: {len(resp.text)}")

# Check response status/text
if "returnValue" in resp.text:
    match_val = re.search(r'name="returnValue"\s+type="hidden"\s+value="([^"]*)"', resp.text)
    if match_val:
        print(f"returnValue in response: {match_val.group(1)}")

# Step 3: Verify deletion
print("\nVerifying deletion...")
user_check = client.find_specific_user(printer_ip, "9999", admin_password=admin_password, logout=True)
if user_check:
    print(f"⚠️  User still found on .253: entry_index={user_check.get('entry_index')}")
else:
    print(f"✅ SUCCESS! User 9999 successfully deleted from .253 address book.")
