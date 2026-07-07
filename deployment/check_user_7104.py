import paramiko
from pathlib import Path
import sys

# Cargar configuración SSH
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

cmd = """docker exec ricoh-backend python -c "
from db.database import SessionLocal
from db.models import User, UserPrinterAssignment
import json

db = SessionLocal()
u = db.query(User).filter(User.codigo_de_usuario == '7104').first()

if u:
    print('USER_FOUND: True')
    print(f'ID: {u.id}')
    print(f'NAME: {u.name}')
    print(f'ACTIVE: {u.is_active}')
    print(f'SMB: {u.smb_path}')
    perms = {
        'func_copier': u.func_copier,
        'func_printer': u.func_printer,
        'func_scanner': u.func_scanner,
        'func_fax': u.func_fax
    }
    print(f'PERMS: {perms}')
    
    assigns = db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == u.id).all()
    print('ASSIGNMENTS:')
    for a in assigns:
        print(f'- Printer ID: {a.printer_id} | Active: {a.is_active} | Entry Index: {a.entry_index} | Perms: copier={a.func_copier}, printer={a.func_printer}, scanner={a.func_scanner}')
else:
    print('USER_FOUND: False')

db.close()
"
"""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))
client.close()
