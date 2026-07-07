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

print("Checking current is_active status of JUAN LIZARAZO (user_id = 3) in database...")
cmd = "docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c \"SELECT name, codigo_de_usuario, is_active FROM users WHERE id = 3;\""
stdin, stdout, stderr = client.exec_command(cmd)

print("Status:")
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
