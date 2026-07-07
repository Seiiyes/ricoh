import paramiko
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("=== Auditando respuestas HTTP del endpoint de comparativa en producción ===")

def query_endpoint(start_a, end_a, start_b, end_b):
    print(f"\n--- Comparando Periodo A ({start_a} a {end_a}) vs Periodo B ({start_b} a {end_b}) ---")
    
    # Construimos la query curl al contenedor backend
    # Como la API requiere autenticación, podemos hacer un query directo con python dentro del contenedor de backend para evitar token
    py_cmd = f"""
docker exec -t ricoh-backend python -c "
import json
from db.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
res = db.execute(
    text('SELECT * FROM get_comparativa_periodos(\\'2026-06-19\\', \\'2026-06-19\\', \\'{start_b}\\', \\'{end_b}\\')')
).fetchall()
data = [
    {{
        'indicador': r.indicador,
        'periodoA': int(r.periodo_a),
        'periodoB': int(r.periodo_b),
        'variacion': float(r.variacion)
    }}
    for r in res
]
print(json.dumps(data, indent=2))
"
"""
    stdin, stdout, stderr = client.exec_command(py_cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    print(out)

# 1. Junio vs Mayo
query_endpoint('2026-06-19', '2026-06-19', '2026-05-20', '2026-05-20')

# 2. Junio vs Abril
query_endpoint('2026-06-19', '2026-06-19', '2026-04-21', '2026-04-21')

# 3. Junio vs Marzo
query_endpoint('2026-06-19', '2026-06-19', '2026-03-12', '2026-03-12')

client.close()
