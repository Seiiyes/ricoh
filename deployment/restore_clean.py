#!/usr/bin/env python3
"""
restore_clean.py
================
Limpia el schema remoto completamente y restaura el backup limpio.
"""
import subprocess, paramiko, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
REMOTE_HOST, REMOTE_SSH_USER, REMOTE_SSH_PASS = load_ssh_config()
REMOTE_CONTAINER= "ricoh-postgres"
REMOTE_DB       = "ricoh_fleet"
REMOTE_USER     = "ricoh_admin"
REMOTE_PASS     = "ricoh_secure_2024"

GREEN  = "\033[92m"; YELLOW = "\033[93m"; CYAN = "\033[96m"; RESET = "\033[0m"
def log(m):  print(f"{GREEN}  [OK] {m}{RESET}", flush=True)
def warn(m): print(f"{YELLOW}  [!]  {m}{RESET}", flush=True)
def info(m): print(f"{CYAN}  -->  {m}{RESET}", flush=True)

# Encontrar el backup mas reciente
backups = sorted(Path("backups").glob("ricoh_backup_*.sql"), reverse=True)
if not backups:
    print("ERROR: No hay backups en carpeta 'backups/'"); sys.exit(1)
DUMP_FILE = backups[0]
REMOTE_DUMP = f"/home/{REMOTE_SSH_USER}/{DUMP_FILE.name}"
print(f"\n  Usando backup: {DUMP_FILE} ({DUMP_FILE.stat().st_size/1024:.1f} KB)\n")

# Conectar SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(REMOTE_HOST, username=REMOTE_SSH_USER, password=REMOTE_SSH_PASS,
               timeout=15, allow_agent=False, look_for_keys=False)
log("Conexion SSH establecida")

def run(cmd, timeout=120):
    ch = client.get_transport().open_session()
    ch.set_combine_stderr(True)
    ch.exec_command(cmd)
    out = b''
    deadline = time.time() + timeout
    while True:
        if ch.recv_ready(): out += ch.recv(4096)
        if ch.exit_status_ready() and not ch.recv_ready(): break
        if time.time() > deadline: break
        time.sleep(0.1)
    out += ch.recv(65535)
    ch.close()
    return ch.recv_exit_status(), out.decode('utf-8', errors='replace').strip()

def sudo(cmd, timeout=120):
    return run(f"echo '{REMOTE_SSH_PASS}' | sudo -S {cmd} 2>&1", timeout=timeout)

def psql(sql, timeout=60):
    return sudo(f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -c \"{sql}\" 2>&1", timeout=timeout)

def psql_postgres(sql, timeout=60):
    return sudo(f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d postgres -c \"{sql}\" 2>&1", timeout=timeout)

# ============================================================
# PASO 1: Limpiar schema completamente con CASCADE
# ============================================================
print(f"\n{CYAN}  [PASO 1] Limpiando schema con CASCADE...{RESET}")
info("Terminando conexiones activas...")
code, out = psql_postgres(
    f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{REMOTE_DB}' AND pid <> pg_backend_pid();"
)
log("Conexiones terminadas")

info("DROP SCHEMA public CASCADE + RECREAR...")
code, out = psql("DROP SCHEMA public CASCADE;")
lines = [l for l in out.split('\n') if 'contraseña' not in l.lower()]
print(f"    {chr(10).join(lines[:3])}")

code, out = psql("CREATE SCHEMA public;")
lines = [l for l in out.split('\n') if 'contraseña' not in l.lower()]
print(f"    {chr(10).join(lines[:3])}")

code, out = psql("GRANT ALL ON SCHEMA public TO public;")
code, out = psql(f"GRANT ALL ON SCHEMA public TO {REMOTE_USER};")
log("Schema limpio y recreado")

# ============================================================
# PASO 2: Generar dump NUEVO sin --clean (solo estructura + datos)
# ============================================================
print(f"\n{CYAN}  [PASO 2] Generando dump limpio (sin --clean)...{RESET}")
import os
CLEAN_DUMP = Path(f"backups/{DUMP_FILE.stem}_clean.sql")
env = os.environ.copy()
env["PGPASSWORD"] = "ricoh_secure_2024"

with open(CLEAN_DUMP, "w", encoding="utf-8") as f:
    result = subprocess.run(
        ["docker", "exec", "ricoh-postgres", "pg_dump",
         "-U", REMOTE_USER, "-d", REMOTE_DB,
         "--no-owner", "--no-acl"],
        stdout=f, stderr=subprocess.PIPE, env=env, text=True
    )

size_kb = CLEAN_DUMP.stat().st_size / 1024
log(f"Dump limpio: {CLEAN_DUMP.name} ({size_kb:.1f} KB)")

# ============================================================
# PASO 3: Transferir dump limpio
# ============================================================
print(f"\n{CYAN}  [PASO 3] Transfiriendo dump al servidor...{RESET}")
REMOTE_CLEAN_DUMP = f"/home/{REMOTE_SSH_USER}/{CLEAN_DUMP.name}"
info(f"Subiendo {CLEAN_DUMP.name}...")
sftp = client.open_sftp()
sftp.put(str(CLEAN_DUMP), REMOTE_CLEAN_DUMP)
sftp.close()
log(f"Transferido: {REMOTE_CLEAN_DUMP}")

# ============================================================
# PASO 4: Restaurar
# ============================================================
print(f"\n{CYAN}  [PASO 4] Restaurando datos...{RESET}")
info("Copiando dump al contenedor...")
code, out = sudo(f"docker cp {REMOTE_CLEAN_DUMP} {REMOTE_CONTAINER}:/tmp/{CLEAN_DUMP.name}")
log("Dump en el contenedor")

info("Ejecutando psql restore...")
code, out = sudo(
    f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -f /tmp/{CLEAN_DUMP.name} 2>&1",
    timeout=300
)
lines = [l for l in out.split('\n') if l.strip() and 'contraseña' not in l.lower()]
errors = [l for l in lines if 'ERROR' in l]

if errors:
    warn(f"{len(errors)} errores durante restore:")
    for e in errors[:5]: print(f"    {e}")
else:
    log("Restore sin errores")

# ============================================================
# PASO 5: Verificar datos
# ============================================================
print(f"\n{CYAN}  [PASO 5] Verificando datos restaurados...{RESET}")
tables_to_check = [
    'users', 'printers', 'empresas', 'contadores_impresora',
    'contadores_usuario', 'centro_costos', 'admin_users',
    'network_credentials', 'smb_servers'
]

print(f"\n  {'Tabla':<35} {'Registros':>10}")
print(f"  {'-'*45}")
total_records = 0
for t in tables_to_check:
    code2, out2 = sudo(
        f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -t -c 'SELECT COUNT(*) FROM {t};' 2>&1"
    )
    cnt_lines = [l.strip() for l in out2.split('\n') if l.strip() and l.strip().isdigit()]
    cnt = int(cnt_lines[0]) if cnt_lines else 0
    total_records += cnt
    marker = f"{GREEN}[OK]{RESET}" if cnt > 0 else f"{YELLOW}[ ]{RESET}"
    print(f"  {marker} {t:<31} {cnt:>10}")

# Limpiar archivos temporales
sudo(f"docker exec {REMOTE_CONTAINER} rm -f /tmp/{CLEAN_DUMP.name}")
sudo(f"rm -f {REMOTE_CLEAN_DUMP}")

client.close()

print(f"\n{GREEN}{'='*60}")
print(f"  MIGRACION COMPLETADA")
print(f"{'='*60}")
print(f"  Total registros en servidor: {total_records}")
print(f"  Backup guardado en:          {DUMP_FILE}")
print(f"  Acceso DBeaver:")
print(f"    Host:     {REMOTE_HOST}")
print(f"    Puerto:   5433")
print(f"    DB:       {REMOTE_DB}")
print(f"    Usuario:  {REMOTE_USER}")
print(f"    Password: {REMOTE_PASS}")
print(f"{'='*60}{RESET}\n")
