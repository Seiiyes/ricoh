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

print("Starting production server health verification...")

# Comando 1: Revisar estado de contenedores
check_containers = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Comando 2: Comprobar que Nginx responda y devuelva index.html (frontend)
check_frontend_http = "curl -sI http://localhost | grep HTTP"

# Comando 3: Comprobar el log de errores del backend de las últimas 50 líneas
check_backend_logs = "docker logs --tail 30 ricoh-backend"

print("\n--- Container Status ---")
stdin, stdout, stderr = client.exec_command(check_containers)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n--- Frontend Web Server Port 80 response ---")
stdin, stdout, stderr = client.exec_command(check_frontend_http)
print(stdout.read().decode('utf-8', errors='replace'))

print("\n--- Backend Container Logs (Last 30 lines) ---")
stdin, stdout, stderr = client.exec_command(check_backend_logs)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
