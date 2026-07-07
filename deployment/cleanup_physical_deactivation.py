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

print("Starting background script to physically disable permissions on printers for ALL inactive users...")

# Script de migración y corrección de permisos físicos en los equipos Ricoh
cleanup_physical_script = """
cat << 'EOF' > /tmp/cleanup_physical_printers.py
import sys
import os
import time
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, UserPrinterAssignment, Printer
from services.ricoh_web_client import get_ricoh_web_client

engine = create_engine('postgresql://ricoh_admin:ricoh_secure_2024@ricoh-postgres:5432/ricoh_fleet')
Session = sessionmaker(bind=engine)
db = Session()

# 1. Obtener todas las asignaciones de usuarios inactivos
inactive_assignments = db.query(UserPrinterAssignment).join(User).filter(User.is_active == False).all()
print(f"Total assignments to disable physically: {len(inactive_assignments)}")

client = get_ricoh_web_client()
disabled_permissions = {k: False for k in ['copiadora', 'copiadora_color', 'escaner', 'impresora', 'impresora_color', 'document_server', 'fax', 'navegador']}

for assoc in inactive_assignments:
    user = assoc.user
    printer = assoc.printer
    if not printer or not assoc.entry_index:
        continue
    
    print(f"\\nProcessing User: {user.name} | Printer: {printer.hostname} ({printer.ip_address}) | Index: {assoc.entry_index}")
    
    # Intentar desactivar físicamente en la impresora
    attempts = 0
    max_attempts = 3
    success = False
    
    while attempts < max_attempts:
        attempts += 1
        try:
            client.reset_session()
            pwd = printer.admin_password or ""
            res = client.set_user_functions(
                printer.ip_address, 
                assoc.entry_index, 
                disabled_permissions, 
                admin_password=pwd,
                set_password=False
            )
            if res is True:
                success = True
                print(f"   ✅ Successfully disabled physically (attempt {attempts})")
                break
            elif res in ["BUSY", "TIMEOUT"]:
                print(f"   ⚠️ Device busy/timeout (attempt {attempts}). Waiting 5s...")
                time.sleep(5)
            else:
                print(f"   ❌ Failed with status: {res} (attempt {attempts})")
        except Exception as e:
            print(f"   ❌ Exception on attempt {attempts}: {str(e)}")
            time.sleep(2)
            
    if success:
        # Poner todos los permisos en false en la base de datos local para mantener consistencia absoluta
        assoc.func_copier = False
        assoc.func_copier_color = False
        assoc.func_printer = False
        assoc.func_printer_color = False
        assoc.func_document_server = False
        assoc.func_fax = False
        assoc.func_scanner = False
        assoc.func_browser = False
        assoc.is_active = False
        db.commit()

db.close()
print("\\n🎉 Physical cleanup process completed.")
EOF
docker cp /tmp/cleanup_physical_printers.py ricoh-backend:/app/cleanup_physical_printers.py
docker exec -t ricoh-backend python /app/cleanup_physical_printers.py
"""

stdin, stdout, stderr = client.exec_command(cleanup_physical_script)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
