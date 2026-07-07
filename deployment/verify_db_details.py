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

print("Fetching complete details for June 19, 2026 closures directly from production DB...")

# Script SQL para traer el detalle de los totalizadores de cada impresora
db_query = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    cm.id as cierre_id,
    p.serial_number,
    p.location,
    cm.fecha_inicio,
    cm.fecha_fin,
    cm.total_paginas,
    cm.total_copiadora,
    cm.total_impresora,
    cm.total_escaner,
    cm.total_fax,
    cm.diferencia_total as diff_paginas,
    cm.diferencia_copiadora as diff_copiadora,
    cm.diferencia_impresora as diff_impresora,
    cm.diferencia_escaner as diff_escaner,
    cm.diferencia_fax as diff_fax
FROM cierres_mensuales cm
INNER JOIN printers p ON p.id = cm.printer_id
WHERE cm.fecha_fin = '2026-06-19'
ORDER BY p.id;
"
"""

stdin, stdout, stderr = client.exec_command(db_query)
print(stdout.read().decode('utf-8', errors='replace'))
client.close()
