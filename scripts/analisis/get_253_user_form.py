"""
Fetch edit user form for 192.168.91.253 and print all inputs/checkboxes.
"""
import sys
sys.path.insert(0, '/app')

import re
from bs4 import BeautifulSoup
from services.ricoh_web_client import get_ricoh_web_client
from db.database import SessionLocal
from db.repository import PrinterRepository

printer_ip = "192.168.91.253"
entry_index = "00001" # YESICA GARCIA is at index 00001

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
print(f"wimToken: {wim_token}")

# Load batch 1
ajax_url = f"http://{printer_ip}/web/entry/es/address/adrsListLoadEntry.cgi"
client.session.post(ajax_url, data={'wimToken': wim_token, 'listCountIn': '50', 'getCountIn': '1'}, headers={
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': list_url
}, timeout=30)

# Request the edit user form
edit_url = f"http://{printer_ip}/web/entry/es/address/adrsGetUser.cgi"
form_data = {
    'wimToken': wim_token,
    'mode': 'MODUSER',
    'outputSpecifyModeIn': 'PROGRAMMED',
    'inputSpecifyModeIn': 'READ',
    'entryIndexIn': entry_index
}
headers = {
    'Referer': list_url,
    'Content-Type': 'application/x-www-form-urlencoded',
}

resp = client.session.post(edit_url, data=form_data, headers=headers, timeout=30)
print(f"Form status: {resp.status_code}")

with open("/tmp/user_form_253.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Saved edit user form HTML to /tmp/user_form_253.html")

soup = BeautifulSoup(resp.text, 'html.parser')
# Find all inputs
inputs = soup.find_all('input')
print(f"\n--- Total inputs found: {len(inputs)} ---")
checkboxes = []
for inp in inputs:
    name = inp.get('name')
    t = inp.get('type')
    val = inp.get('value')
    if t == 'checkbox':
        checkboxes.append(inp)
        is_checked = inp.has_attr('checked') or inp.get('checked') == 'checked'
        print(f"Checkbox: name='{name}', value='{val}', checked={is_checked}")
    elif name in ['entryNameIn', 'userCodeIn', 'folderPathNameIn']:
        print(f"Text Input: name='{name}', value='{val}'")

print(f"\n--- Total checkboxes: {len(checkboxes)} ---")
