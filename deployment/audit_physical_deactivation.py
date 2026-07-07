import paramiko
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("Starting live audit of physical permissions on Ricoh devices for inactive users...")

# Script que corre dentro del contenedor ricoh-backend para consultar físicamente en vivo las impresoras 
# de los usuarios desactivados y reportar sus permisos actuales en hardware.
audit_script = """
cat << 'EOF' > /tmp/audit_live_printers.py
import sys
import os
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, UserPrinterAssignment, Printer
from services.ricoh_web_client import get_ricoh_web_client

engine = create_engine('postgresql://ricoh_admin:ricoh_secure_2024@ricoh-postgres:5432/ricoh_fleet')
Session = sessionmaker(bind=engine)
db = Session()

# 1. Obtener usuarios inactivos con asignaciones
inactive_assignments = db.query(UserPrinterAssignment).join(User).filter(User.is_active == False).all()
print(f"Checking {len(inactive_assignments)} assignments of inactive users in physical hardware...")

client = get_ricoh_web_client()
for assoc in inactive_assignments:
    user = assoc.user
    printer = assoc.printer
    if not printer or not assoc.entry_index:
        continue
    
    print(f"\\n🔍 [IN LIVE AUDIT] User: {user.name} ({user.codigo_de_usuario}) | Printer: {printer.hostname} ({printer.ip_address}) | Index: {assoc.entry_index}")
    try:
        client.reset_session()
        pwd = printer.admin_password or ""
        details = client._get_user_details(printer.ip_address, assoc.entry_index, fast_sync=False, admin_password=pwd)
        if details and 'permisos' in details:
            p = details['permisos']
            active_perms = [k for k, v in p.items() if v]
            if active_perms:
                print(f"   ⚠️ WARNING: Active physical permissions found in hardware: {active_perms}")
            else:
                print(f"   ✅ OK: 0 physical permissions active in hardware.")
        else:
            print(f"   ❌ ERROR: Could not retrieve live permissions from device web page.")
    except Exception as e:
        print(f"   ❌ EXCEPTION connecting to device: {str(e)}")

db.close()
EOF
docker cp /tmp/audit_live_printers.py ricoh-backend:/app/audit_live_printers.py
docker exec -t ricoh-backend python /app/audit_live_printers.py
"""

stdin, stdout, stderr = client.exec_command(audit_script)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
