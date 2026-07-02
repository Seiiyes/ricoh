#!/usr/bin/env python3
"""Consulta y verifica usuario 7104 con API y BD"""
import paramiko
import sys
import io
import time
import json
import subprocess
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=30):
    ch = client.get_transport().open_session()
    ch.set_combine_stderr(True)
    ch.exec_command(cmd)
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
    return out.decode('utf-8', errors='replace').strip()

PG = "docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet"
BASE = "http://localhost:8000"

print("="*60)

print("[1] Usuario 7104 en BD (por codigo_de_usuario)")
u7104 = run(f"""{PG} -c "SELECT id, name, codigo_de_usuario, is_active, empresa_id FROM users WHERE codigo_de_usuario='7104';" 2>&1""")
print(u7104)

print("\n[2] Asignaciones del usuario 7104 con impresoras")
assign = run(f"""{PG} -c "SELECT u.name, u.codigo_de_usuario, u.is_active, p.ip, p.nombre as impresora, upa.is_active as asignacion_activa, upa.func_copier, upa.func_printer, upa.func_scanner FROM users u JOIN user_printer_assignments upa ON upa.user_id = u.id JOIN printers p ON p.id = upa.printer_id WHERE u.codigo_de_usuario='7104';" 2>&1""")
print(assign)

print("\n[3] Estado is_active y activo en asignaciones de usuario 7104")
count = run(f"""{PG} -c "SELECT u.name, u.is_active as user_active, COUNT(upa.id) as total_assign, SUM(CASE WHEN upa.is_active THEN 1 ELSE 0 END) as active_assign FROM users u LEFT JOIN user_printer_assignments upa ON upa.user_id = u.id WHERE u.codigo_de_usuario='7104' GROUP BY u.name, u.is_active;" 2>&1""")
print(count)

# Intentar login con password encriptado para ver qué hay en la BD
print("\n[4] Intentando login con diferentes passwords via API")
for pwd in ["Admin1234!", "admin", "ricoh2024", "Ricoh2024!", "admin1234"]:
    result = run(f"""curl -s -X POST {BASE}/auth/login -H "Content-Type: application/json" -d '{{"username":"superadmin","password":"{pwd}"}}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK:' + d.get('access_token','')[:20] if 'access_token' in d else 'FAIL:' + str(d.get('detail','')))" 2>&1""")
    print(f"  pwd={pwd}: {result}")

client.close()
print("="*60)
