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

print("Updating June closure dates in production database...")

# Query para cambiar la fecha_inicio a 2026-06-19 para los cierres del 19 de junio
db_query = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
UPDATE cierres_mensuales 
SET fecha_inicio = '2026-06-19' 
WHERE fecha_fin = '2026-06-19';
"
"""

stdin, stdout, stderr = client.exec_command(db_query)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
