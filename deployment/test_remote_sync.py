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
    deadline = time.time() + 180  # allow up to 3 mins
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
    return out.decode('utf-8', errors='replace').strip()

print("="*60)
print(f"RUNNING PARALLEL SYNC PERFORMANCE TEST ON: {HOST}")
print("="*60)

# Create a test script directly inside the backend container or remote host and execute it
test_python_code = """
import requests
import json
import time

# Read superadmin password from backend folder
try:
    with open('/app/.superadmin_password', 'r') as f:
        password = f.read().strip()
except Exception as e:
    print("Error reading password:", e)
    exit(1)

# Login
login_url = "http://localhost:8000/auth/login"
payload = {
    "username": "superadmin",
    "password": password
}
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

print("Authenticating with superadmin...")
response = requests.post(login_url, data=payload, headers=headers)
if response.status_code != 200:
    print("Authentication failed:", response.status_code, response.text)
    exit(1)

token = response.json().get("access_token")
print("Authentication successful.")

# Call sync users
sync_url = "http://localhost:8000/discovery/sync-users-from-printers"
auth_headers = {
    "Authorization": f"Bearer {token}"
}

print("Initiating synchronization (measuring time)...")
start_time = time.time()
sync_response = requests.post(sync_url, headers=auth_headers, timeout=240)
duration = time.time() - start_time

print("\\nSync status code:", sync_response.status_code)
print("Sync duration: {:.2f} seconds".format(duration))

try:
    res_json = sync_response.json()
    print("\\nSync response details:")
    print("- Success:", res_json.get("success"))
    print("- Message:", res_json.get("message"))
    print("- Total unique users:", res_json.get("total_usuarios_unicos"))
    print("- Printers scanned count:", len(res_json.get("printers_scanned", [])))
    for p in res_json.get("printers_scanned", []):
        err = " | Error: " + p['error'] if 'error' in p else ""
        print("  * {} ({}): {} users{}".format(p.get('hostname'), p.get('ip'), p.get('users_count'), err))
except Exception as e:
    print("Error parsing response:", e)
    print("Response text:", sync_response.text[:500])
"""

# Write code to a file inside the backend container and run it
write_cmd = f"cat << 'EOF' > /home/odootic/ricoh-app/backend/test_parallel_sync.py\n{test_python_code}\nEOF"
run(write_cmd)

# Run the python script inside the docker container so it has direct backend access
print("Running test inside backend container...")
print(run("docker exec ricoh-backend python /app/test_parallel_sync.py"))

# Clean up
run("rm -f /home/odootic/ricoh-app/backend/test_parallel_sync.py")

client.close()
print("="*60)
