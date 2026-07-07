import paramiko
import sys
import io
import csv
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("Starting Data Integrity Audit: CSV vs Production Database...")

# Python script to run inside backend container to calculate sums from database and compare with CSVs
audit_script = """
cat << 'EOF' > /tmp/audit_integrity_internal.py
import os
import csv
import re
import sys
sys.path.append('/app')

from db.models import CierreMensual, CierreMensualUsuario, Printer, User
from db.database import SessionLocal

def limpiar_string(val):
    if not val:
        return ""
    return re.sub(r"[\\'\\[\\]\\\"\\(\\)]", "", str(val)).strip()

def parse_int(val):
    if not val or val == "-" or val == "---":
        return 0
    try:
        val_clean = str(val).replace(",", "").replace(".", "").strip()
        return int(val_clean)
    except:
        return 0

db = SessionLocal()
try:
    csv_mappings = [
        ("E174M210096 19.06.2026.csv", "E174M210096"),
        ("E174MA11130 19.06.2026.csv", "E174MA11130"),
        ("E176M460020 19.06.2026.csv", "E176M460020"),
        ("G986XA16285 19.06.2026.csv", "G986XA16285"),
        ("W533L900719 19.06.2026.csv", "W533L900719")
    ]
    
    print("-" * 110)
    print(f"{'Printer Serial':<15} | {'CSV Users':<10} | {'DB Users':<10} | {'CSV Total Pages':<15} | {'DB Sum Pages':<15} | {'Discrepancy':<12}")
    print("-" * 110)

    for filename, serial in csv_mappings:
        filepath = f"/app/docs/{filename}"
        if not os.path.exists(filepath):
            print(f"❌ File {filename} not found!")
            continue
            
        # 1. Sumar totales del CSV
        csv_users_count = 0
        csv_total_pages = 0
        
        with open(filepath, mode='r', encoding='utf-8') as csv_file:
            first_line = csv_file.readline()
            csv_file.seek(0)
            is_ecologico = "Código de usuario" in first_line or "Nº de registro" in first_line
            reader = csv.DictReader(csv_file)
            
            for row in reader:
                if is_ecologico:
                    raw_user_code = row.get('Código de usuario') or row.get('código de usuario')
                    user_code = limpiar_string(raw_user_code)
                    if not user_code or user_code == "-" or user_code == "Total" or user_code == "total":
                        continue
                    total_paginas = parse_int(row.get('Total páginas impresión', 0))
                else:
                    raw_user_code = row.get('Usuario') or row.get('usuario')
                    user_code = limpiar_string(raw_user_code)
                    if not user_code or user_code == "Total" or user_code == "total":
                        continue
                    total_paginas = parse_int(row.get('Total impresiones', 0))
                
                csv_users_count += 1
                csv_total_pages += total_paginas
                
        # 2. Sumar totales de la base de datos para esta impresora y cierre
        printer = db.query(Printer).filter(Printer.serial_number == serial).first()
        if not printer:
            print(f"{serial:<15} | Printer not found in DB")
            continue
            
        cierre = db.query(CierreMensual).filter(
            CierreMensual.printer_id == printer.id,
            CierreMensual.fecha_fin == '2026-06-19'
        ).first()
        
        if not cierre:
            print(f"{serial:<15} | Closure not found for 2026-06-19")
            continue
            
        db_users_count = len(cierre.usuarios)
        db_sum_pages = sum(u.total_paginas for u in cierre.usuarios)
        discrepancy = csv_total_pages - db_sum_pages
        
        status = "✅ OK" if discrepancy == 0 and csv_users_count == db_users_count else "⚠️ DIFF"
        print(f"{serial:<15} | {csv_users_count:<10} | {db_users_count:<10} | {csv_total_pages:<15,} | {db_sum_pages:<15,} | {discrepancy:<12} ({status})")
        
    print("-" * 110)
    
except Exception as e:
    print(f"❌ Error during audit: {e}")
finally:
    db.close()
EOF
docker cp /tmp/audit_integrity_internal.py ricoh-backend:/app/audit_integrity_internal.py
docker exec -t ricoh-backend python /app/audit_integrity_internal.py
"""

stdin, stdout, stderr = client.exec_command(audit_script)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
