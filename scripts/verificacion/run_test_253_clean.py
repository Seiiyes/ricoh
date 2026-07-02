"""
Clean session, provision dummy user, and delete it on printer 192.168.91.253.
Handles retries if printer is busy.
"""
import sys
sys.path.insert(0, '/app')

import time
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

# Force logout first to clear any locked WIM sessions
print("Forcing WIM logout...")
client._logout(printer_ip)
time.sleep(2)

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

entry_index = None
for attempt in range(1, 4):
    print(f"\nProvision attempt {attempt}...")
    client.reset_session()
    res = client.provision_user(printer_ip, user_config, admin_password=admin_password, logout=False)
    print(f"Provision result: {res}")
    if res == "BUSY":
        print("Printer busy, forcing logout and waiting 5 seconds...")
        client._logout(printer_ip)
        time.sleep(5)
    elif isinstance(res, tuple) and res[0] is True:
        entry_index = res[1]
        break
    else:
        print(f"Unexpected result: {res}")
        time.sleep(3)

if not entry_index:
    print("Could not provision dummy user on .253")
    sys.exit(1)

print(f"\nDummy user provisioned successfully at entry_index={entry_index}")

# Perform deletion
print("\nProceeding to delete dummy user using adrsDeleteEntry.cgi...")
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
    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsConfirmDelete.cgi",
    'Content-Type': 'application/x-www-form-urlencoded'
}

resp = client.session.post(delete_url, data=payload, headers=headers, timeout=30)
print(f"Delete response status: {resp.status_code}")
print(f"Delete response length: {len(resp.text)}")

if "returnValue" in resp.text:
    match_val = re.search(r'name="returnValue"\s+type="hidden"\s+value="([^"]*)"', resp.text)
    if match_val:
        print(f"returnValue in delete response: {match_val.group(1)}")

# Verify deletion
print("\nVerifying deletion...")
user_check = client.find_specific_user(printer_ip, "9999", admin_password=admin_password, logout=True)
if user_check:
    print(f"⚠️  User still found: entry_index={user_check.get('entry_index')}")
else:
    print(f"✅ SUCCESS! User 9999 successfully deleted from .253 address book.")
