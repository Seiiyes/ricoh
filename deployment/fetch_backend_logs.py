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

print("Fetching last 150 lines from ricoh-backend logs...")
stdin, stdout, stderr = client.exec_command("docker logs ricoh-backend --tail 150 2>&1")
logs = stdout.read().decode('utf-8', errors='replace')

print("\n=== RECENT BACKEND LOGS ===")
print(logs)

client.close()
