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

print("Reading superadmin password from server...")
# El archivo .superadmin_password está en el directorio del backend /app o similar, o en el host en la carpeta del backend.
# Miremos la carpeta del proyecto en el host del servidor.
# Normalmente el docker-compose monta el volumen. Busquemos en la carpeta /home/... o /opt/... o en la carpeta donde está el backend.
# Miremos la salida de pwd o ls en el host.
stdin, stdout, stderr = client.exec_command("find / -name .superadmin_password 2>/dev/null")
paths = stdout.read().decode('utf-8', errors='replace').strip().split('\n')

if paths and paths[0]:
    print(f"Found path: {paths[0]}")
    stdin, stdout, stderr = client.exec_command(f"cat {paths[0]}")
    print("Password:", stdout.read().decode('utf-8', errors='replace').strip())
else:
    print("File .superadmin_password not found, checking inside docker container...")
    stdin, stdout, stderr = client.exec_command("docker exec ricoh-backend cat /app/.superadmin_password 2>/dev/null")
    pwd = stdout.read().decode('utf-8', errors='replace').strip()
    if pwd:
        print("Password from container:", pwd)
    else:
        print("Could not find password.")

client.close()
