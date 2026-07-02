"""
Inspect adrsList.cgi HTML to find how deletion is handled on the printer list page.
"""
import sys
sys.path.insert(0, '/app')

import re
from bs4 import BeautifulSoup
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

print("Authenticating...")
if not client._authenticate(printer_ip, admin_password):
    print("Authentication failed")
    sys.exit(1)

list_url = f"http://{printer_ip}/web/entry/es/address/adrsList.cgi"
resp = client.session.get(list_url, timeout=30)
print(f"List page status: {resp.status_code}")

with open('/tmp/adrsList.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)
print("Saved list page to /tmp/adrsList.html")

soup = BeautifulSoup(resp.text, 'html.parser')

print("\n--- Forms found in list page ---")
forms = soup.find_all('form')
for i, f in enumerate(forms):
    print(f"Form {i}: action={f.get('action')}, name={f.get('name')}, id={f.get('id')}")
    # Print inputs in form
    inputs = f.find_all('input')
    for inp in inputs:
        if inp.get('type') != 'hidden':
            print(f"  Input: type={inp.get('type')}, name={inp.get('name')}, value={inp.get('value')}")

print("\n--- Searching for 'eliminar' or 'borrar' or 'delete' in list page text ---")
for text in soup.find_all(text=True):
    if any(word in text.lower() for word in ['eliminar', 'borrar', 'delete']):
        print(f"Text match: {text.strip()} (Parent tag: {text.parent.name})")

print("\n--- Searching for checkboxes/buttons in table rows ---")
# Checkboxes typically select users for deletion
checkboxes = soup.find_all('input', {'type': 'checkbox'})
print(f"Found {len(checkboxes)} checkboxes:")
for cb in checkboxes[:10]:
    print(f"  Checkbox: name={cb.get('name')}, value={cb.get('value')}, id={cb.get('id')}")

buttons = soup.find_all('input', {'type': 'button'}) + soup.find_all('input', {'type': 'submit'}) + soup.find_all('button')
print(f"Found {len(buttons)} buttons:")
for btn in buttons[:10]:
    print(f"  Button: type={btn.get('type')}, name={btn.get('name')}, value={btn.get('value') or btn.text}")
