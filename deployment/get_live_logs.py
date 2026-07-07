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

print("Checking docker logs for 'user-details' or code '48555'...")
stdin, stdout, stderr = client.exec_command("docker logs --tail 2000 ricoh-backend")
logs = stdout.read().decode('utf-8', errors='replace')
err_logs = stderr.read().decode('utf-8', errors='replace')

lines_with_details = [line for line in logs.split('\n') if 'user-details' in line or '48555' in line or 'live-permissions' in line]
print(f"Found {len(lines_with_details)} matching lines:")
for line in lines_with_details[-20:]:  # mostrar últimas 20 líneas
    print(line)

client.close()
