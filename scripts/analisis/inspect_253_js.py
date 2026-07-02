"""
Download and inspect xjs files from printer 192.168.91.253 to see if its Delete flow differs.
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

# Download adrsListAll.xjs from .253
resp = client.session.get(f"http://{printer_ip}/web/entry/es/address/adrsListAll.xjs", timeout=30)
with open("/tmp/adrsListAll_253.xjs", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Downloaded adrsListAll.xjs from .253")

# Search for DATAIDX_ENTRYID definition in adrsListAll_253.xjs
print("\n--- DATAIDX_ENTRYID definition in .253 ---")
for line in resp.text.split('\n'):
    if 'DATAIDX_ENTRYID' in line or 'var DATAIDX_' in line:
        print("  ", line.strip())

# Search for Delete function in adrsListAll_253.xjs
print("\n--- Delete function in .253 ---")
match_del = re.search(r'function\s+Delete\s*\(', resp.text)
if match_del:
    start_idx = match_del.start()
    brace_count = 0
    end_idx = -1
    for i in range(start_idx, len(resp.text)):
        if resp.text[i] == '{':
            brace_count += 1
        elif resp.text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    if end_idx != -1:
        print(resp.text[start_idx:end_idx])
    else:
        print("Delete matching brace not found")
else:
    print("Delete not found")
