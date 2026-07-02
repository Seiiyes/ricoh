#!/usr/bin/env python3
"""Verificación completa: login API + usuario 7104 + asignaciones"""
import paramiko
import sys
import io
import time
import json
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
PWD = "ricoh2026"

print("="*60)

# 1. Login
print("[1] LOGIN API")
login_raw = run(f"""curl -s -X POST {BASE}/auth/login -H "Content-Type: application/json" -d '{{"username":"superadmin","password":"{PWD}"}}'""")
try:
    token = json.loads(login_raw).get('access_token')
    if token:
        print("Login: OK")
    else:
        print(f"Login FAIL: {login_raw[:200]}")
        client.close()
        sys.exit(1)
except Exception as e:
    print(f"Error: {e} | raw={login_raw[:200]}")
    client.close()
    sys.exit(1)

# 2. GET /users/ con trailing slash (evitar 307)
print("\n[2] GET /users/?search=7104")
resp = run(f"""curl -s -L "{BASE}/users/?search=7104&per_page=10" -H "Authorization: Bearer {token}" """)
print(f"Raw resp: {resp[:500]}")
try:
    data = json.loads(resp)
    users = data.get('users', data.get('items', data.get('usuarios', [])))
    if not users and isinstance(data, list):
        users = data
    print(f"Total: {data.get('total', len(users))}")
    for u in users:
        print(f"  id={u.get('id')} | codigo={u.get('codigo_de_usuario')} | name={u.get('name')} | is_active={u.get('is_active')}")
    uid = users[0].get('id') if users else None
except Exception as e:
    print(f"Parse error: {e}")
    uid = None

# 3. BD: usuario 7104 + asignaciones (columnas correctas)
print("\n[3] BD: usuario 7104 + asignaciones")
detail = run(f"""{PG} -c "SELECT u.id, u.name, u.codigo_de_usuario, u.is_active, p.ip_address, p.detected_model, p.hostname, upa.is_active as asig_activa, upa.entry_index, upa.func_copier, upa.func_copier_color, upa.func_printer, upa.func_scanner FROM users u JOIN user_printer_assignments upa ON upa.user_id = u.id JOIN printers p ON p.id = upa.printer_id WHERE u.codigo_de_usuario='7104';" 2>&1""")
print(detail)

# 4. Obtener ID de BD si no se encontró en la búsqueda API
if not uid:
    uid_bd = run(f"""{PG} -c "SELECT id FROM users WHERE codigo_de_usuario='7104';" 2>&1""")
    print(f"\n[4] ID en BD para 7104: {uid_bd}")
    if uid_bd:
        lines = [l.strip() for l in uid_bd.split('\n') if l.strip().isdigit()]
        if lines:
            uid = int(lines[0])

if uid:
    print(f"\n[5] GET /users/{uid}/")
    det_resp = run(f"""curl -s -L "{BASE}/users/{uid}/" -H "Authorization: Bearer {token}" """)
    try:
        det = json.loads(det_resp)
        print(f"  name={det.get('name')} | is_active={det.get('is_active')}")
    except:
        print(det_resp[:600])

    print(f"\n[6] GET /provisioning/user/{uid}")
    prov_resp = run(f"""curl -s -L "{BASE}/provisioning/user/{uid}" -H "Authorization: Bearer {token}" """)
    try:
        prov = json.loads(prov_resp)
        print(f"  status success? = {prov.get('user_id') == uid}")
        printers = prov.get('printers', [])
        print(f"  Printers in provisioning status: {len(printers)}")
        for p in printers:
            print(f"    id={p.get('id')} | ip={p.get('ip_address')} | entry_index={p.get('entry_index')} | status={p.get('status')} | permisos={p.get('permisos')}")
    except Exception as e:
        print(f"  Error parsing: {e}")
        print(prov_resp[:2000])
    # Query details for all assigned printers
    print(f"\n[7] Query /discovery/user-details for all assigned printers:")
    test_printers = [
        ("192.168.91.250", "00231"),
        ("192.168.91.253", "00195"),
        ("192.168.110.250", "00087"),
        ("192.168.91.252", "00089"),
        ("192.168.91.251", "00256")
    ]
    for ip, entry in test_printers:
        print(f"  Querying {ip} (entry {entry})...")
        det_user_resp = run(f"""curl -s -L "{BASE}/discovery/user-details?printer_ip={ip}&entry_index={entry}" -H "Authorization: Bearer {token}" """)
        print(f"    Response: {det_user_resp[:400]}")
else:
    print("\nNo se pudo encontrar el ID del usuario 7104")

client.close()
print("="*60)
