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

print("Checking user 7104 in database...")
# Usar -t para forzar TTY o llamar directamente sin psql interactivo si falla
cmd = "docker exec ricoh-postgres psql -U postgres -d ricoh -t -c \"SELECT id, name, codigo_de_usuario, is_active FROM users WHERE codigo_de_usuario = '7104';\""
stdin, stdout, stderr = client.exec_command(cmd)
print("Stdout:", stdout.read().decode('utf-8', errors='replace'))
print("Stderr:", stderr.read().decode('utf-8', errors='replace'))

print("\nListing some users in database to see codes format...")
cmd_list = "docker exec ricoh-postgres psql -U postgres -d ricoh -t -c \"SELECT id, name, codigo_de_usuario, is_active FROM users LIMIT 10;\""
stdin, stdout, stderr = client.exec_command(cmd_list)
print("Stdout:", stdout.read().decode('utf-8', errors='replace'))

client.close()
