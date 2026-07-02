"""
Debug script to test DELETEUSER flow on Ricoh printer.
Captures the full HTML response to understand what the printer expects.
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

import re
import requests
from bs4 import BeautifulSoup

# Test target
printer_ip = "192.168.91.252"
entry_index = "00089"
admin_password = None  # Will use the printer's admin_password from DB

from db.database import SessionLocal
from db import models
from db.repository import PrinterRepository

db = SessionLocal()
printer = PrinterRepository.get_by_ip(db, printer_ip)
admin_password = printer.admin_password if printer else None
db.close()

print(f"Admin password type: {type(admin_password)}")
print(f"Admin password: {'(set)' if admin_password else '(None)'}")

# Create a session (mimicking what the web client does)
session = requests.Session()
timeout = 30

# Step 1: Authenticate
print(f"\n--- Step 1: Authenticating to {printer_ip} ---")
# Try default password first
login_url = f"http://{printer_ip}/web/entry/es/login/loginCcNotCredit.cgi"
login_data = {
    'wimToken': '',
    'privilege': 'USERADMIN',
    'loginName': 'admin',
    'loginPassword': admin_password or '',
    'encrypted': 'false',
}
resp = session.post(login_url, data=login_data, timeout=timeout, allow_redirects=True)
print(f"Login response: {resp.status_code}")

if resp.status_code != 200 or 'logout' not in resp.text.lower():
    # Try alternative
    login_data['loginPassword'] = 'Ricoh@2024'
    resp = session.post(login_url, data=login_data, timeout=timeout, allow_redirects=True)
    print(f"Alternative login response: {resp.status_code}")

# Step 2: Get wimToken from adrsList.cgi
print(f"\n--- Step 2: Getting wimToken from adrsList.cgi ---")
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = session.get(list_url, timeout=timeout)
print(f"List page status: {list_resp.status_code}")

wim_token = ""
match = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text)
if match:
    wim_token = match.group(1)
    print(f"wimToken: {wim_token[:4]}...{wim_token[-4:]}")
else:
    print("ERROR: No wimToken found!")
    sys.exit(1)

# Step 3: Load the batch for the entry_index
print(f"\n--- Step 3: Loading batch for entry_index {entry_index} ---")
ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
batch = (int(entry_index) // 50) + 1
print(f"Batch: {batch}")
ajax_data = {
    'wimToken': wim_token,
    'listCountIn': '50',
    'getCountIn': str(batch)
}
ajax_resp = session.post(ajax_url, data=ajax_data, headers={
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded'
}, timeout=timeout)
print(f"Batch load status: {ajax_resp.status_code}")
print(f"Batch response snippet: {ajax_resp.text[:200]}")

# Step 4: Try DELETEUSER on adrsGetUser.cgi
print(f"\n--- Step 4: Getting DELETEUSER form ---")
edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
form_data = {
    'wimToken': wim_token,
    'mode': 'DELETEUSER',
    'outputSpecifyModeIn': 'PROGRAMMED',
    'inputSpecifyModeIn': 'READ',
    'entryIndexIn': entry_index
}
headers = {
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}
response = session.post(edit_url, data=form_data, headers=headers, timeout=timeout)
print(f"DELETEUSER form status: {response.status_code}")
print(f"\nFirst 500 chars of response:")
print(response.text[:500])
print(f"\n--- Checking for key strings ---")
print(f"BADFLOW: {'BADFLOW' in response.text}")
print(f"wimToken in response: {bool(re.search(r'wimToken', response.text))}")
print(f"Delete button: {bool(re.search(r'DELETEUSER|delete|Delete', response.text))}")

# Save full response for analysis
with open('/tmp/delete_form_debug.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print(f"\nFull response saved to /tmp/delete_form_debug.html")

# Try without batch loading first
print(f"\n--- Step 4b: Trying DELETEUSER WITHOUT batch loading ---")
# Fresh session
session2 = requests.Session()
resp2 = session2.post(login_url, data=login_data, timeout=timeout, allow_redirects=True)
list_resp2 = session2.get(list_url, timeout=timeout)
wim_token2 = ""
match2 = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp2.text)
if match2:
    wim_token2 = match2.group(1)
    print(f"wimToken2: {wim_token2[:4]}...{wim_token2[-4:]}")

form_data2 = {
    'wimToken': wim_token2,
    'mode': 'DELETEUSER',
    'entryIndexIn': entry_index
}
response2 = session2.post(edit_url, data=form_data2, headers={
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}, timeout=timeout)
print(f"Direct DELETEUSER form status: {response2.status_code}")
print(f"BADFLOW: {'BADFLOW' in response2.text}")
print(f"First 300 chars: {response2.text[:300]}")

with open('/tmp/delete_form_debug2.html', 'w', encoding='utf-8') as f:
    f.write(response2.text)
print(f"\nResponse2 saved to /tmp/delete_form_debug2.html")
