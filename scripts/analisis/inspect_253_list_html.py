"""
Download adrsList.cgi from .253 and inspect MainForm structure and checkbox names.
"""
import sys
sys.path.insert(0, '/app')

import re
from bs4 import BeautifulSoup
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

if not client._authenticate(printer_ip, admin_password):
    print("Authentication failed")
    sys.exit(1)

resp = client.session.get(f"http://{printer_ip}/web/entry/es/address/adrsList.cgi", timeout=30)
with open("/tmp/adrsList_253.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Downloaded adrsList.cgi from .253")

soup = BeautifulSoup(resp.text, 'html.parser')
# Find MainForm or form with action/id containing MainForm
forms = soup.find_all('form')
print("\n--- Forms in .253 adrsList.cgi ---")
for i, f in enumerate(forms):
    print(f"Form {i}: action={f.get('action')}, name={f.get('name')}, id={f.get('id')}")
    # Hidden inputs
    hiddens = [inp.get('name') for inp in f.find_all('input', {'type': 'hidden'})]
    print(f"  Hidden inputs: {hiddens}")

# Let's inspect some of the checkboxes in the page
checkboxes = soup.find_all('input', {'type': 'checkbox'})
print(f"\n--- Checkboxes (first 10) in .253 ---")
for cb in checkboxes[:10]:
    print(f"  name={cb.get('name')}, value={cb.get('value')}, id={cb.get('id')}")
