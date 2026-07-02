#!/usr/bin/env python3
import paramiko
import sys
import io
import time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)

def run(cmd):
    ch = client.get_transport().open_session()
    ch.set_combine_stderr(True)
    ch.exec_command(f"echo '{PASS}' | sudo -S {cmd} 2>&1")
    out = b''
    deadline = time.time() + 30
    while True:
        if ch.recv_ready():
            out += ch.recv(4096)
        if ch.exit_status_ready() and not ch.recv_ready():
            break
        if time.time() > deadline:
            break
        time.sleep(0.1)
    remaining = ch.recv(65535)
    if remaining:
        out += remaining
    ch.close()
    lines = [l for l in out.decode('utf-8', errors='replace').split('\n') if '[sudo]' not in l and 'password for' not in l.lower()]
    return '\n'.join(lines).strip()

print("="*60)
print(f"UPLOADING INSPECTION SCRIPT AND RUNNING ON: {HOST}")
print("="*60)

# Upload the file
sftp = client.open_sftp()
local_path = Path(__file__).parent.parent / "backend" / "inspect_7104.py"
remote_path = "/home/odootic/ricoh-app/backend/inspect_7104.py"
print(f"Uploading {local_path.name} -> {remote_path}")
sftp.put(str(local_path), remote_path)
sftp.close()

# Execute inside the container
query_cmd = "docker compose -f /home/odootic/ricoh-app/docker-compose.yml exec -T backend python inspect_7104.py"
print(run(query_cmd))

# Cleanup
run("rm -f /home/odootic/ricoh-app/backend/inspect_7104.py")

client.close()
print("="*60)


