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

print("Listing May 20, 2026 closure totalizers per printer...")

db_query = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT p.id, p.serial_number, p.location, cm.total_paginas, cm.total_copiadora, cm.total_impresora, cm.total_escaner, cm.total_fax
FROM cierres_mensuales cm
INNER JOIN printers p ON p.id = cm.printer_id
WHERE cm.fecha_fin = '2026-05-20';
"
"""

stdin, stdout, stderr = client.exec_command(db_query)
print(stdout.read().decode('utf-8', errors='replace'))
client.close()
