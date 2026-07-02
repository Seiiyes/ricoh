"""
Debug v2: Use the ricoh_web_client's authentication and batch loading,
then try DELETEUSER with different approaches.
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

import re
from bs4 import BeautifulSoup
from services.ricoh_web_client import get_ricoh_web_client, RicohWebClient
from db.database import SessionLocal
from db.repository import PrinterRepository

# Test target
printer_ip = "192.168.91.252"
entry_index = "00089"

db = SessionLocal()
printer = PrinterRepository.get_by_ip(db, printer_ip)
admin_password = printer.admin_password if printer else None
db.close()

client = get_ricoh_web_client()

print("=== Debug DELETEUSER Flow ===\n")

# Reset and authenticate using the proper method
client.reset_session()

print("Step 1: Authenticating...")
auth_result = client._authenticate(printer_ip, admin_password)
print(f"Auth result: {auth_result}")

if not auth_result:
    print("AUTH FAILED")
    sys.exit(1)

# Get wimToken from adrsList.cgi
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = client.session.get(list_url, timeout=30)
print(f"\nStep 2: adrsList.cgi status: {list_resp.status_code}")

wim_token = ""
match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
if match:
    wim_token = match.group(1)
    client._wim_tokens[printer_ip] = wim_token
    print(f"wimToken: {wim_token[:4]}...{wim_token[-4:]}")

# Try the batch loading - use _warmup_entry_session approach (loadBatch)
print(f"\nStep 3a: Loading entry via _warmup_entry_session...")
client._warmup_entry_session(printer_ip, entry_index)

# Now try DELETEUSER
print(f"\nStep 4a: Trying DELETEUSER with READ mode...")
edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
form_data = {
    'wimToken': wim_token,
    'mode': 'DELETEUSER',
    'outputSpecifyModeIn': 'PROGRAMMED',
    'inputSpecifyModeIn': 'READ',
    'entryIndexIn': entry_index
}
response = client.session.post(edit_url, data=form_data, headers={
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}, timeout=30)
print(f"Response status: {response.status_code}")
print(f"BADFLOW: {'BADFLOW' in response.text}")
print(f"First 500 chars: {response.text[:500]}")

with open('/tmp/debug_delete_v2a.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Saved to /tmp/debug_delete_v2a.html")

# If BADFLOW, try without READ mode
if 'BADFLOW' in response.text:
    print(f"\nStep 4b: Trying DELETEUSER WITHOUT READ mode...")
    # Refresh wimToken
    list_resp2 = client.session.get(list_url, timeout=30)
    match2 = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp2.text)
    if match2:
        wim_token = match2.group(1)
    
    form_data2 = {
        'wimToken': wim_token,
        'mode': 'DELETEUSER',
        'entryIndexIn': entry_index
    }
    response2 = client.session.post(edit_url, data=form_data2, headers={
        'Referer': list_url,
        'Content-Type': 'application/x-www-form-urlencoded',
    }, timeout=30)
    print(f"Response2 status: {response2.status_code}")
    print(f"BADFLOW: {'BADFLOW' in response2.text}")
    print(f"First 500 chars: {response2.text[:500]}")
    
    with open('/tmp/debug_delete_v2b.html', 'w', encoding='utf-8') as f:
        f.write(response2.text)
    print("Saved to /tmp/debug_delete_v2b.html")

# Try batch load approach from set_user_functions (listCountIn/getCountIn)
print(f"\nStep 5: Trying batch load with listCountIn/getCountIn...")
ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
batch = (int(entry_index) // 50) + 1
ajax_data = {
    'wimToken': wim_token,
    'listCountIn': '50',
    'getCountIn': str(batch)
}
ajax_resp = client.session.post(ajax_url, data=ajax_data, headers={
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded'
}, timeout=30)
print(f"Batch load status: {ajax_resp.status_code}")
print(f"Batch response: {ajax_resp.text[:200]}")

# Refresh wimToken
list_resp3 = client.session.get(list_url, timeout=30)
match3 = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp3.text)
if match3:
    wim_token = match3.group(1)
    print(f"Refreshed wimToken: {wim_token[:4]}...{wim_token[-4:]}")

# Try DELETEUSER again
print(f"\nStep 6: Trying DELETEUSER after batch load...")
form_data3 = {
    'wimToken': wim_token,
    'mode': 'DELETEUSER',
    'outputSpecifyModeIn': 'PROGRAMMED',
    'inputSpecifyModeIn': 'READ',
    'entryIndexIn': entry_index
}
response3 = client.session.post(edit_url, data=form_data3, headers={
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}, timeout=30)
print(f"Response3 status: {response3.status_code}")
print(f"BADFLOW: {'BADFLOW' in response3.text}")
print(f"First 500 chars: {response3.text[:500]}")

with open('/tmp/debug_delete_v2c.html', 'w', encoding='utf-8') as f:
    f.write(response3.text)
print("Saved to /tmp/debug_delete_v2c.html")

print("\n=== Debug complete ===")
