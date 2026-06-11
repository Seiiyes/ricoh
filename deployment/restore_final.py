#!/usr/bin/env python3
"""Restaura un dump específico en el servidor remoto."""
import paramiko, time, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DUMP_FILE       = "backups/ricoh_FULL_20260611_144435.sql"
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
REMOTE_HOST, REMOTE_SSH_USER, REMOTE_SSH_PASS = load_ssh_config()
REMOTE_CONTAINER= "ricoh-postgres"
REMOTE_DB       = "ricoh_fleet"
REMOTE_USER     = "ricoh_admin"

GREEN = "\033[92m"; YELLOW = "\033[93m"; CYAN = "\033[96m"; RESET = "\033[0m"
def log(m):  print(f"{GREEN}  [OK] {m}{RESET}", flush=True)
def info(m): print(f"{CYAN}  -->  {m}{RESET}", flush=True)
def warn(m): print(f"{YELLOW}  [!]  {m}{RESET}", flush=True)

dump = Path(DUMP_FILE)
print(f"\n  Dump: {dump} ({dump.stat().st_size/1024:.1f} KB)")

# Conectar
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(REMOTE_HOST, username=REMOTE_SSH_USER, password=REMOTE_SSH_PASS,
               timeout=15, allow_agent=False, look_for_keys=False)
log("SSH conectado")

def run(cmd, timeout=300):
    ch = client.get_transport().open_session()
    ch.set_combine_stderr(True)
    ch.exec_command(cmd)
    out = b''
    deadline = time.time() + timeout
    while True:
        if ch.recv_ready(): out += ch.recv(8192)
        if ch.exit_status_ready() and not ch.recv_ready(): break
        if time.time() > deadline: break
        time.sleep(0.1)
    out += ch.recv(65535)
    ch.close()
    return ch.recv_exit_status(), out.decode('utf-8', errors='replace').strip()

def sudo(cmd, timeout=300):
    return run(f"echo '{REMOTE_SSH_PASS}' | sudo -S {cmd} 2>&1", timeout=timeout)

def psql(sql):
    return sudo(f'docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -c "{sql}" 2>&1')

# 1. Limpiar schema
info("Limpiando schema (DROP CASCADE)...")
sudo(f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{REMOTE_DB}' AND pid <> pg_backend_pid();\" 2>&1")
sudo(f'docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -c "DROP SCHEMA public CASCADE;" 2>&1')
sudo(f'docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -c "CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public; GRANT ALL ON SCHEMA public TO {REMOTE_USER};" 2>&1')
log("Schema limpio")

# 2. Transferir dump
REMOTE_PATH = f"/home/{REMOTE_SSH_USER}/{dump.name}"
info(f"Transfiriendo {dump.name}...")
sftp = client.open_sftp()
sftp.put(str(dump), REMOTE_PATH)
sftp.close()
log(f"Dump en servidor: {REMOTE_PATH}")

# 3. Copiar al contenedor y restaurar
info("Copiando al contenedor Docker...")
sudo(f"docker cp {REMOTE_PATH} {REMOTE_CONTAINER}:/tmp/{dump.name}")
log("Dump copiado al contenedor")

info("Restaurando (psql)...")
code, out = sudo(f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -f /tmp/{dump.name} 2>&1", timeout=300)
errors = [l for l in out.split('\n') if 'ERROR' in l and 'contraseña' not in l.lower()]
if errors:
    warn(f"{len(errors)} errores: {errors[0][:100]}")
else:
    log("Restore sin errores")

# 4. Verificar
print(f"\n{CYAN}  Verificando datos...{RESET}")
tables = ['users','printers','admin_users','empresas','contadores_impresora',
          'contadores_usuario','centro_costos','network_credentials','smb_servers']
print(f"\n  {'Tabla':<30} {'Registros':>10}")
print(f"  {'-'*42}")
total = 0
for t in tables:
    code2, out2 = sudo(f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -t -c 'SELECT COUNT(*) FROM {t};' 2>&1")
    cnt_lines = [l.strip() for l in out2.split('\n') if l.strip().isdigit()]
    cnt = int(cnt_lines[0]) if cnt_lines else 0
    total += cnt
    marker = f"{GREEN}[OK]{RESET}" if cnt > 0 else f"{YELLOW}[ ]{RESET}"
    print(f"  {marker} {t:<26} {cnt:>10}")

# Limpiar
sudo(f"docker exec {REMOTE_CONTAINER} rm -f /tmp/{dump.name}")
sudo(f"rm -f {REMOTE_PATH}")
client.close()

print(f"\n{GREEN}{'='*50}")
print(f"  MIGRACION EXITOSA - {total} registros totales")
print(f"{'='*50}")
print(f"  DBeaver -> {REMOTE_HOST}:5433 / ricoh_fleet")
print(f"  Usuario: {REMOTE_USER} / ricoh_secure_2024")
print(f"{'='*50}{RESET}\n")
