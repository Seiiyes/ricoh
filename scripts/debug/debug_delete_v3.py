"""
Debug v3: Try posting DIRECTLY to adrsSetUser.cgi with DELETEUSER (skip GET form).
Based on analysis of the BADFLOW response which shows the printer knows DELETEUSER mode.
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

import re
from bs4 import BeautifulSoup
from services.ricoh_web_client import get_ricoh_web_client
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
client.reset_session()

print("Step 1: Authenticating...")
auth_result = client._authenticate(printer_ip, admin_password)
print(f"Auth result: {auth_result}")
if not auth_result:
    sys.exit(1)

# Get wimToken from adrsList.cgi
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = client.session.get(list_url, timeout=30)
print(f"List page status: {list_resp.status_code}")

wim_token = ""
match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
if match:
    wim_token = match.group(1)
    print(f"wimToken: {wim_token[:4]}...{wim_token[-4:]}")

# Load the batch
ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
batch = (int(entry_index) // 50) + 1
ajax_data = {'wimToken': wim_token, 'listCountIn': '50', 'getCountIn': str(batch)}
ajax_resp = client.session.post(ajax_url, data=ajax_data, headers={
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded'
}, timeout=30)
print(f"Batch load status: {ajax_resp.status_code}")

# Refresh wimToken
list_resp2 = client.session.get(list_url, timeout=30)
match2 = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp2.text)
if match2:
    wim_token = match2.group(1)
    print(f"Refreshed wimToken: {wim_token[:4]}...{wim_token[-4:]}")

# APPROACH: Direct POST to adrsSetUser.cgi with DELETEUSER (skip GET form)
print(f"\n--- Attempt: Direct POST to adrsSetUser.cgi with DELETEUSER ---")
update_url = f"http://{printer_ip}/web/entry/es/address/adrsSetUser.cgi"

# Minimal DELETEUSER payload (similar to what browser would send from confirmation page)
payload = [
    ('wimToken', wim_token),
    ('mode', 'DELETEUSER'),
    ('inputSpecifyModeIn', 'WRITE'),
    ('listUpdateIn', 'UPDATE'),
    ('entryIndexIn', entry_index),
    ('outputSpecifyModeIn', ''),
    ('pageSpecifiedIn', ''),
    ('pageNumberIn', ''),
    ('wayFrom', f'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
    ('wayTo', 'adrsList.cgi'),
]

update_headers = {
    'Referer': f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi",
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded'
}

resp = client.session.post(update_url, data=payload, headers=update_headers, timeout=30, allow_redirects=True)
print(f"Response status: {resp.status_code}")
print(f"BADFLOW: {'BADFLOW' in resp.text}")
print(f"Length: {len(resp.text)}")
print(f"First 500 chars: {resp.text[:500]}")

with open('/tmp/debug_delete_v3a.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print("Saved to /tmp/debug_delete_v3a.html")

# Check if success - look for adrsList content (redirect success)
if resp.status_code in [200, 302] and 'BADFLOW' not in resp.text:
    print("\n✅ SUCCESS - No BADFLOW detected!")
    
    # Verify user is gone
    print("\nVerifying by searching for user...")
    user_check = client.find_specific_user(printer_ip, "7104", admin_password=admin_password)
    if user_check:
        print(f"⚠️  User still found: entry_index={user_check.get('entry_index')}")
    else:
        print(f"✅ User no longer found in printer address book!")
else:
    print(f"\n❌ FAILED - BADFLOW or error")
    
    # Try another approach: also get the MODUSER form first (to 'warm up' the session state)
    print("\n--- Attempt 2: MODUSER READ first, then switch to DELETEUSER ---")
    
    # Reset and re-authenticate
    client.reset_session()
    client._authenticate(printer_ip, admin_password)
    list_resp = client.session.get(list_url, timeout=30)
    match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
    wim_token = match.group(1) if match else ""
    
    # Load batch
    client.session.post(ajax_url, data={'wimToken': wim_token, 'listCountIn': '50', 'getCountIn': str(batch)}, 
                       headers={'X-Requested-With': 'XMLHttpRequest', 'Referer': list_url}, timeout=30)
    
    # First do a MODUSER READ to warm up
    edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
    form_response = client.session.post(edit_url, data={
        'wimToken': wim_token,
        'mode': 'MODUSER',
        'outputSpecifyModeIn': 'PROGRAMMED',
        'inputSpecifyModeIn': 'READ',
        'entryIndexIn': entry_index
    }, headers={'Referer': list_url, 'Content-Type': 'application/x-www-form-urlencoded'}, timeout=30)
    
    soup = BeautifulSoup(form_response.text, 'html.parser')
    token_input = soup.find('input', {'name': 'wimToken'})
    if token_input:
        wim_token = token_input.get('value', wim_token)
        print(f"New wimToken after MODUSER READ: {wim_token[:4]}...{wim_token[-4:]}")
    
    print(f"MODUSER READ BADFLOW: {'BADFLOW' in form_response.text}")
    
    # Now try DELETEUSER
    payload2 = [
        ('wimToken', wim_token),
        ('mode', 'DELETEUSER'),
        ('inputSpecifyModeIn', 'WRITE'),
        ('listUpdateIn', 'UPDATE'),
        ('entryIndexIn', entry_index),
        ('outputSpecifyModeIn', ''),
        ('pageSpecifiedIn', ''),
        ('pageNumberIn', ''),
        ('wayFrom', f'adrsGetUser.cgi?outputSpecifyModeIn=SETTINGS'),
        ('wayTo', 'adrsList.cgi'),
    ]
    
    resp2 = client.session.post(update_url, data=payload2, headers={
        'Referer': edit_url,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
    }, timeout=30, allow_redirects=True)
    
    print(f"Attempt 2 Response status: {resp2.status_code}")
    print(f"BADFLOW: {'BADFLOW' in resp2.text}")
    print(f"First 500 chars: {resp2.text[:500]}")
    
    with open('/tmp/debug_delete_v3b.html', 'w', encoding='utf-8') as f:
        f.write(resp2.text)
    print("Saved to /tmp/debug_delete_v3b.html")

print("\n=== Debug v3 complete ===")
