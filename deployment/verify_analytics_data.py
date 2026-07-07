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

print("Listing closure periods now in DB...")

# Script para ver la lista de periodos únicos de cierre en la base de datos
db_list_periods = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT DISTINCT fecha_inicio, fecha_fin, COUNT(*) as registros_cierre
FROM cierres_mensuales
GROUP BY fecha_inicio, fecha_fin
ORDER BY fecha_fin DESC;
"
"""

# Script para ver el consumo comparativo de Junio vs Mayo con la nueva fecha
db_consumption_june = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT 
    u.name as usuario,
    SUM(CASE WHEN cm.fecha_inicio = '2026-06-19' THEN cmu.total_paginas ELSE 0 END) as absoluto_june,
    SUM(CASE WHEN cm.fecha_inicio = '2026-05-20' THEN cmu.total_paginas ELSE 0 END) as absoluto_may,
    SUM(CASE WHEN cm.fecha_inicio = '2026-06-19' THEN cmu.consumo_total ELSE 0 END) as consumo_june
FROM cierres_mensuales_usuarios cmu
INNER JOIN cierres_mensuales cm ON cm.id = cmu.cierre_mensual_id
INNER JOIN users u ON u.id = cmu.user_id
GROUP BY u.name
HAVING SUM(CASE WHEN cm.fecha_inicio = '2026-06-19' THEN cmu.total_paginas ELSE 0 END) > 0
ORDER BY absoluto_june DESC
LIMIT 10;
"
"""

print("\n--- Current Periods ---")
stdin, stdout, stderr = client.exec_command(db_list_periods)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n--- June vs May comparative sample (Top 10 absolute pages users) ---")
stdin, stdout, stderr = client.exec_command(db_consumption_june)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
