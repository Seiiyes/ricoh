"""
List all users on printer 192.168.91.253 whose names contain TEST or PRUEBA.
"""
import sys
sys.path.insert(0, '/app')

import re
import ast
import json
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

# Read all users
users = client.read_users_from_printer(printer_ip, fast_list=True, admin_password=admin_password, logout=True)
print(f"Total users found: {len(users)}")

test_users = []
for u in users:
    name = u.get('nombre', '')
    code = u.get('codigo', '')
    if any(w in name.lower() or w in code.lower() for w in ['test', 'prueba', '9999']):
        test_users.append(u)

print(f"Found {len(test_users)} test/dummy users:")
for u in test_users:
    print(f"  Name: '{u.get('nombre')}', Code: '{u.get('codigo')}', Index: '{u.get('entry_index')}'")
