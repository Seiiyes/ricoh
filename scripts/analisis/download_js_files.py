"""
Download and inspect xjs files from Ricoh printer.
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

# Fetch xjs files
base_url = f"http://{printer_ip}/web/entry/es/address/"
xjs_files = ["adrsBase.xjs", "adrsListAll.xjs", "adrsUserWizard.xjs"]

for fn in xjs_files:
    url = base_url + fn
    resp = client.session.get(url, timeout=30)
    print(f"File {fn}: status={resp.status_code}, length={len(resp.text)}")
    with open(f"/tmp/{fn}", "w", encoding="utf-8") as f:
        f.write(resp.text)

print("\n--- Searching for 'function Delete' in adrsListAll.xjs ---")
with open("/tmp/adrsListAll.xjs", "r", encoding="utf-8") as f:
    list_all_js = f.read()

delete_func = re.findall(r'function\s+Delete\s*\([\s\S]*?\{([\s\S]*?)\}', list_all_js)
if delete_func:
    print("Found function Delete():")
    # Clean and show lines
    lines = [l.strip() for l in delete_func[0].split('\n') if l.strip()]
    for l in lines[:40]:
        print(f"  {l}")
    print("  ...")
else:
    print("Function Delete() not found in adrsListAll.xjs")

# Find where else it might be
for fn in xjs_files:
    with open(f"/tmp/{fn}", "r", encoding="utf-8") as f:
        content = f.read()
    matches = re.findall(r'function\s+Delete\s*\([\s\S]*?\{([\s\S]*?)\}', content)
    if matches:
        print(f"Found function Delete() in {fn}!")
        lines = [l.strip() for l in matches[0].split('\n') if l.strip()]
        for l in lines[:40]:
            print(f"  {l}")
        print("  ...")
