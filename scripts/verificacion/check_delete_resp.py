"""
Perform delete request and dump the full response to analyze why it didn't delete the user.
"""
import sys
sys.path.insert(0, '/app')

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

if not client._authenticate(printer_ip, admin_password):
    print("Authentication failed")
    sys.exit(1)

# Get fresh wimToken
list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
list_resp = client.session.get(list_url, timeout=30)
wim_token = re.search(r'name="wimToken"\s+value="(\d+)"', list_resp.text).group(1)
print(f"wimToken: {wim_token}")

# Let's perform the delete request and write the HTML
delete_url = f"http://{printer_ip}/web/entry/es/address/adrsDeleteEntries.cgi"
files = {
    'entryIndex': (None, f"{entry_index},"),
    'wimToken': (None, wim_token)
}
headers = {
    'Referer': list_url,
    'X-Requested-With': 'XMLHttpRequest'
}
resp = client.session.post(delete_url, files=files, headers=headers, timeout=30)

with open("/tmp/delete_resp.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Saved delete response to /tmp/delete_resp.html")

# Analyze response text
if "BADFLOW" in resp.text:
    print("Found BADFLOW in response")
if "error" in resp.text.lower() or "error" in resp.text.lower():
    print("Found 'error' in response text")
# Print any hidden inputs
from bs4 import BeautifulSoup
soup = BeautifulSoup(resp.text, 'html.parser')
inputs = soup.find_all('input')
print("Hidden and visible inputs in response:")
for inp in inputs:
    print(f"  name={inp.get('name')}, type={inp.get('type')}, value={inp.get('value')}")
