"""
Download ajax.js and read ajax_async.
"""
import sys
sys.path.insert(0, '/app')

import re
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

resp = client.session.get(f"http://{printer_ip}/scripts/ajax.js", timeout=30)
with open("/tmp/ajax.js", "w", encoding="utf-8") as f:
    f.write(resp.text)
print(f"Downloaded ajax.js, status={resp.status_code}")

# Find ajax_async
match = re.search(r'function\s+ajax_async\s*\(', resp.text)
if match:
    start_idx = match.start()
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
        print("ajax_async matching brace not found")
else:
    print("ajax_async not found")
