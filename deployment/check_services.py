#!/usr/bin/env python3
import paramiko, time, sys, io
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
    # Clean up sudo output
    lines = [l for l in out.decode('utf-8', errors='replace').split('\n') if '[sudo]' not in l and 'password for' not in l.lower()]
    return '\n'.join(lines).strip()

print("\n" + "="*60)
print(f"  VERIFICANDO CONTENEDORES Y PUERTOS EN REMOTE: {HOST}")
print("="*60)

print("\n[CONTENEDORES CORRIENDO]")
print(run("docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"))

print("\n[ENTORNO DE ricoh-backend]")
print(run("docker exec ricoh-backend env | grep -E 'CORS_ORIGINS|DATABASE_URL|REDIS_URL|ENVIRONMENT'"))

print("\n[ENTORNO DE ricoh-frontend]")
print(run("docker exec ricoh-frontend env"))

print("\n[VERIFICACION DE PUERTOS (netstat)]")
print(run("netstat -tuln | grep -E ':80 |:8000|:5433|:5432' || ss -tuln | grep -E ':80|:8000|:5433|:5432'"))

client.close()
print("\n" + "="*60)
