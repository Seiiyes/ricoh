import paramiko
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("Fetching backend logs (last 200 lines)...")
stdin, stdout, stderr = client.exec_command("docker logs ricoh-backend --tail 200 2>&1")
logs = stdout.read().decode('utf-8', errors='replace')

print("\n=== ALL RECENT BACKEND LOGS ===")
keywords = ["401", "403", "500", "ERROR", "error", "WARN", "redis", "Redis", "session", "auth", "login", "Unauthorized"]
for line in logs.splitlines():
    if any(q.lower() in line.lower() for q in keywords):
        print(line)

print("\n=== RAW LAST 50 LINES ===")
lines = logs.splitlines()
for line in lines[-50:]:
    print(line)

client.close()
