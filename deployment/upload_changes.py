#!/usr/bin/env python3
import paramiko
import sys
import io
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

LOCAL_DIR = Path(__file__).parent.parent
REMOTE_DIR = f"/home/{USER}/ricoh-app"

files_to_upload = [
    "backend/api/discovery.py",
    "backend/services/ricoh_web_client.py",
    "backend/api/provisioning.py",
    "backend/services/provisioning.py",
    "backend/db/repository.py",
    "backend/db/models.py",
    "backend/services/user_sync_service.py",
    "backend/api/users.py",
    "backend/services/ricoh_password_flow.py",
    "backend/services/retry_strategy.py",
    "backend/api/counters.py",
    "backend/api/printers.py",
    "backend/api/schemas.py",
    "backend/check_redis.py",
    "backend/services/auth_service.py",
    "backend/middleware/auth_middleware.py",
    "backend/main.py",
    "backend/tests/test_secure_session_migration.py",
    "src/pages/OverviewDashboard.tsx",
    "src/pages/AnalyticsPage.tsx",
    "src/pages/Dashboard.tsx",
    "src/index.css",
    "src/components/usuarios/AdministracionUsuarios.tsx",
    "src/components/usuarios/ModificarUsuario.tsx",
    "src/components/usuarios/FilaUsuario.tsx",
    "src/components/usuarios/TablaUsuarios.tsx",
    "src/store/useUsuarioStore.ts",
    "src/types/index.ts",
    "src/services/servicioUsuarios.ts",
    "src/services/apiClient.ts",
    "src/services/authService.ts",
    "src/services/printerService.ts",
    "deployment/nginx/conf.d/ricoh.conf"
]

print("="*60)
print(f"CONNECTING TO REMOTE SERVER: {HOST}")
print("="*60)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)

sftp = client.open_sftp()

print("\n[UPLOADING FILES DIRECTLY TO SERVER]")
for rel_path in files_to_upload:
    local_path = LOCAL_DIR / rel_path
    remote_path = f"{REMOTE_DIR}/{rel_path}"
    print(f"Uploading {rel_path} -> {remote_path}")
    sftp.put(str(local_path), remote_path)

sftp.close()
print("Upload complete.")

def run(cmd, timeout=30):
    ch = client.get_transport().open_session()
    ch.set_combine_stderr(True)
    ch.exec_command(f"echo '{PASS}' | sudo -S {cmd} 2>&1")
    out = b''
    deadline = time.time() + timeout
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

print("\n[REBUILDING FRONTEND CONTAINER ON THE SERVER]")
# We use docker compose up --build -d frontend to compile the React app with the new apiClient settings
print(run("docker compose -f /home/odootic/ricoh-app/docker-compose.yml up --build -d frontend", timeout=300))

print("\n[RESTARTING SERVICES ON THE SERVER]")
print(run("docker restart ricoh-backend ricoh-nginx"))

print("\n[CHECKING CONTAINER STATUS]")
print(run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"))

client.close()
print("="*60)
