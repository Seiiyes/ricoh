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
# Usar credenciales reales de docker-compose
cmd = "docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -t -c \"SELECT id, name, codigo_de_usuario, is_active FROM users WHERE codigo_de_usuario = '7104';\""
stdin, stdout, stderr = client.exec_command(cmd)
print("Stdout:", stdout.read().decode('utf-8', errors='replace'))
print("Stderr:", stderr.read().decode('utf-8', errors='replace'))

print("Checking user 7104 printer assignments...")
cmd2 = "docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -t -c \"SELECT u.name, upa.printer_id, upa.is_active, upa.func_copier, upa.func_printer, upa.func_scanner FROM user_printer_assignments upa JOIN users u ON u.id = upa.user_id WHERE u.codigo_de_usuario = '7104';\""
stdin, stdout, stderr = client.exec_command(cmd2)
print("Stdout assignments:", stdout.read().decode('utf-8', errors='replace'))
print("Stderr assignments:", stderr.read().decode('utf-8', errors='replace'))

client.close()
