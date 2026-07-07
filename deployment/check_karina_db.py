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

print("Checking duplicate printer assignments in DB for KARINA MENDEZ...")
cmd = "docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c \"SELECT u.name, upa.id, upa.printer_id, upa.entry_index, upa.is_active FROM user_printer_assignments upa JOIN users u ON u.id = upa.user_id WHERE u.name ILIKE '%KARINA MENDEZ%';\""
stdin, stdout, stderr = client.exec_command(cmd)
print("Assignments:")
print(stdout.read().decode('utf-8', errors='replace'))
print("Errors:")
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
