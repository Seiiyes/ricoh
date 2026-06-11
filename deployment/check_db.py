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
    ch.exec_command(cmd)
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
    return out.decode('utf-8', errors='replace')

def psql(sql):
    cmd = f"echo '{PASS}' | sudo -S docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c \"{sql}\" 2>&1"
    result = run(cmd)
    # Quitar linea de sudo password prompt
    lines = [l for l in result.split('\n') if '[sudo]' not in l and 'password for' not in l.lower()]
    return '\n'.join(lines).strip()

print("\n" + "="*60)
print("  BASE DE DATOS: ricoh_fleet @ 192.168.91.131")
print("="*60)

# 1. Listar tablas
print("\n[TABLAS EXISTENTES]")
r = psql("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;")
print(r)

# 2. Conteo por tabla
print("\n[REGISTROS POR TABLA]")
tables = [
    'users', 'printers', 'admin_users', 'empresas', 'centro_costos',
    'contadores_impresora', 'contadores_usuario', 'network_credentials',
    'smb_servers', 'user_printer_assignments', 'cierres_mensuales',
    'cierres_mensuales_usuarios', 'comparaciones_guardadas', 'auditoria_sistema',
    'admin_sessions', 'admin_audit_log'
]
for t in tables:
    r = psql(f"SELECT COUNT(*) as total FROM {t};")
    lines = [l.strip() for l in r.split('\n') if l.strip() and not l.strip().startswith('-') and 'total' not in l.lower() and 'row' not in l.lower()]
    count = lines[0] if lines else '?'
    print(f"  {t:<30} {count} registros")

# 3. Datos de admin_users
print("\n[DATOS DE admin_users]")
r = psql("SELECT id, username, email, is_active, failed_login_attempts, locked_until FROM admin_users;")
print(r)

client.close()
print("\n" + "="*60)
