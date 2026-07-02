"""
Download adrsBase.xjs from .253 and find ADRS_DELETE value.
"""
import sys
sys.path.insert(0, '/app')

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

if not client._authenticate(printer_ip, admin_password):
    print("Authentication failed")
    sys.exit(1)

resp = client.session.get(f"http://{printer_ip}/web/entry/es/address/adrsBase.xjs", timeout=30)
with open("/tmp/adrsBase_253.xjs", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Downloaded adrsBase.xjs from .253")

# Search in both files for ADRS_DELETE
print("\n--- Searching for ADRS_DELETE value ---")
for fn in ["/tmp/adrsListAll_253.xjs", "/tmp/adrsBase_253.xjs"]:
    with open(fn, "r", encoding="utf-8") as f:
        text = f.read()
    for line in text.split('\n'):
        if 'ADRS_DELETE' in line and ('=' in line or 'var' in line or 'define' in line):
            print(f"  {fn}: {line.strip()}")
