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

print("Searching server logs for DELETE requests, user ID 3 (7104), or deactivation logs...")

# Comando para buscar ocurrencias en el log histórico omitiendo las llamadas de healthcheck (127.0.0.1)
cmd = "docker logs ricoh-backend 2>&1 | grep -v '127.0.0.1' | grep -i -E 'DELETE|deactivate|User ID: 3|7104|error' | tail -n 80"
stdin, stdout, stderr = client.exec_command(cmd)

print("\n=== FILTERED DEACTIVATION LOGS ===")
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
