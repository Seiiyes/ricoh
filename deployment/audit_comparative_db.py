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

print("=== Consultando la firma y retorno de get_comparativa_periodos en la BD de producción ===")

cmd = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT * FROM get_comparativa_periodos('2026-06-19', '2026-06-19', '2026-05-20', '2026-05-20');
"
"""
stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))

print("=== Consultando la definición de la función en Postgres ===")
cmd_def = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT pg_get_functiondef('get_comparativa_periodos'::regproc);
"
"""
stdin2, stdout2, stderr2 = client.exec_command(cmd_def)
print(stdout2.read().decode('utf-8', errors='replace'))

client.close()
