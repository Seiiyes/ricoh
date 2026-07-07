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

print("Checking docker logs for background deactivation tasks...")
# Consulta los logs de docker del contenedor de backend buscando eventos de desactivación física
sql_query = """
docker logs --tail 3000 ricoh-backend 2>&1
"""
stdin, stdout, stderr = client.exec_command(sql_query)
logs = stdout.read().decode('utf-8', errors='replace')

lines_with_deact = [
    line for line in logs.split('\n') 
    if any(keyword in line for keyword in ['BACKGROUND', 'deactivate_user_printers_task', 'Deshabilitando', 'Intento', 'Finished physical'])
]

print(f"Found {len(lines_with_deact)} background deactivation log lines:")
for line in lines_with_deact[-40:]:  # Mostrar últimas 40 líneas
    print(line)

client.close()
