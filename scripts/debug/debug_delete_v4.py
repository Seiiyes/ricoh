"""
Debug v4: Try deleting user from printer using adrsDeleteEntries.cgi with multipart/form-data.
Uses requests files parameter for multipart encoding to avoid external dependencies.
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

import re
from services.ricoh_web_client import get_ricoh_web_client
from db.database import SessionLocal
from db.repository import PrinterRepository

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
    print(f"wimToken: {wim_token}")

if not wim_token:
    print("Failed to get wimToken")
    sys.exit(1)

# Let's perform the delete request using files parameter
delete_url = f"http://{printer_ip}/web/entry/es/address/adrsDeleteEntries.cgi"

# Construct files parameter (sends as multipart/form-data)
files = {
    'entryIndex': (None, f"{entry_index},"),
    'wimToken': (None, wim_token)
}

print(f"\nSending delete request to: {delete_url}")
headers = {
    'Referer': list_url,
    'X-Requested-With': 'XMLHttpRequest'
}

resp = client.session.post(delete_url, files=files, headers=headers, timeout=30)
print(f"Response status: {resp.status_code}")
print(f"Response text length: {len(resp.text)}")
print(f"First 1000 chars of response:")
print(resp.text[:1000])

# Verify user deletion by calling find_specific_user
print("\nVerifying user is deleted...")
user_check = client.find_specific_user(printer_ip, "7104", admin_password=admin_password)
if user_check:
    print(f"⚠️  User still found: entry_index={user_check.get('entry_index')}")
else:
    print(f"✅ SUCCESS! User 7104 no longer found in printer address book.")
