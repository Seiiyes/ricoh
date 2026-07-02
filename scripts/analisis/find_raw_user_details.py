"""
Fetch and print raw AJAX user list from printer to see the exact structure.
"""
import sys
sys.path.insert(0, '/app')

import re
import json
import ast
from services.ricoh_web_client import get_ricoh_web_client
from db.database import SessionLocal
from db.repository import PrinterRepository

printer_ip = "192.168.91.252"

db = SessionLocal()
printer = PrinterRepository.get_by_ip(db, printer_ip)
admin_password = printer.admin_password if printer else None
db.close()

client = get_ricoh_web_client()
client.reset_session()

if not client._authenticate(printer_ip, admin_password):
    print("Authentication failed")
    sys.exit(1)

# Get wimToken
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = client.session.get(list_url, timeout=30)
wim_token = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text).group(1)

# Request batch 1
ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
payload = {
    'wimToken': wim_token,
    'listCountIn': '50',
    'getCountIn': '1'
}
headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': list_url
}
resp = client.session.post(ajax_url, data=payload, headers=headers, timeout=30)
print(f"Status: {resp.status_code}")

try:
    data = ast.literal_eval(resp.text.strip())
except:
    data = json.loads(resp.text.strip().replace("'", '"'))

print(f"\nTotal entries in batch 1: {len(data)}")
print("First 5 entries:")
for i, entry in enumerate(data[:5]):
    print(f"Entry {i}: {entry}")

# Let's search for user 7104 in all batches!
print("\nSearching for user 7104 in all batches...")
found = False
for batch in range(1, 10):
    payload = {
        'wimToken': wim_token,
        'listCountIn': '50',
        'getCountIn': str(batch)
    }
    resp = client.session.post(ajax_url, data=payload, headers=headers, timeout=30)
    if resp.status_code != 200 or not resp.text.strip():
        break
    try:
        batch_data = ast.literal_eval(resp.text.strip())
    except:
        batch_data = json.loads(resp.text.strip().replace("'", '"'))
        
    for entry in batch_data:
        # Check if user code matches 7104 (it could be in entry[4] or entry[8] or entry[3] etc)
        # Let's print the entry if "7104" or "lizarazo" is in it (case-insensitive)
        entry_str = str(entry).lower()
        if '7104' in entry_str or 'lizarazo' in entry_str:
            print(f"Found match in batch {batch}: {entry}")
            found = True
            break
    if found:
        break
