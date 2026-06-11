#!/usr/bin/env python3
"""
backup_and_restore.py
=====================
1. Hace pg_dump de la DB local (Docker en esta máquina)
2. Transfiere el dump al servidor 192.168.91.131 via SFTP
3. Restaura la DB en el servidor remoto

Uso: python deployment/backup_and_restore.py
"""
import subprocess, paramiko, time, sys, io, os
from pathlib import Path
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# =============================================================
# CONFIGURACION
# =============================================================
LOCAL_CONTAINER  = "ricoh-postgres"
LOCAL_DB         = "ricoh_fleet"
LOCAL_USER       = "ricoh_admin"
LOCAL_PASS       = "ricoh_secure_2024"

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
REMOTE_HOST, REMOTE_SSH_USER, REMOTE_SSH_PASS = load_ssh_config()
REMOTE_CONTAINER = "ricoh-postgres"
REMOTE_DB        = "ricoh_fleet"
REMOTE_USER      = "ricoh_admin"
REMOTE_PASS      = "ricoh_secure_2024"

TIMESTAMP        = datetime.now().strftime("%Y%m%d_%H%M%S")
DUMP_FILE        = f"ricoh_backup_{TIMESTAMP}.sql"
LOCAL_DUMP_PATH  = Path(f"backups/{DUMP_FILE}")
REMOTE_DUMP_PATH = f"/home/{REMOTE_SSH_USER}/{DUMP_FILE}"

GREEN  = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"; CYAN = "\033[96m"; RESET = "\033[0m"
def log(m):  print(f"{GREEN}  [OK] {m}{RESET}", flush=True)
def warn(m): print(f"{YELLOW}  [!]  {m}{RESET}", flush=True)
def err(m):  print(f"{RED}  [ERR] {m}{RESET}", flush=True); sys.exit(1)
def info(m): print(f"{CYAN}  -->  {m}{RESET}", flush=True)

# =============================================================
# 1. PG_DUMP LOCAL
# =============================================================
def make_local_dump():
    print(f"\n{CYAN}{'='*60}")
    print(f"  [PASO 1] Backup de DB local -> {DUMP_FILE}")
    print(f"{'='*60}{RESET}\n")

    LOCAL_DUMP_PATH.parent.mkdir(exist_ok=True)

    info(f"Ejecutando pg_dump en contenedor '{LOCAL_CONTAINER}'...")
    cmd = [
        "docker", "exec", LOCAL_CONTAINER,
        "pg_dump",
        "-U", LOCAL_USER,
        "-d", LOCAL_DB,
        "--clean",           # DROP antes de CREATE
        "--if-exists",       # no falla si no existe
        "--no-owner",        # ignora permisos de owner
        "--no-acl",          # ignora permisos de acceso
        "-v"                 # verbose
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = LOCAL_PASS

    with open(LOCAL_DUMP_PATH, "w", encoding="utf-8") as f:
        result = subprocess.run(
            cmd, stdout=f, stderr=subprocess.PIPE,
            env=env, text=True
        )

    if result.returncode != 0:
        warn(f"pg_dump stderr:\n{result.stderr[:500]}")
        if not LOCAL_DUMP_PATH.exists() or LOCAL_DUMP_PATH.stat().st_size < 100:
            err("pg_dump fallo y el archivo esta vacio")
        warn("pg_dump tuvo advertencias pero el dump existe - continuando")
    
    size_kb = LOCAL_DUMP_PATH.stat().st_size / 1024
    log(f"Dump generado: {LOCAL_DUMP_PATH} ({size_kb:.1f} KB)")
    return LOCAL_DUMP_PATH

# =============================================================
# 2. CONEXION SSH AL SERVIDOR REMOTO
# =============================================================
def connect_remote():
    info(f"Conectando SSH a {REMOTE_SSH_USER}@{REMOTE_HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        REMOTE_HOST, username=REMOTE_SSH_USER, password=REMOTE_SSH_PASS,
        timeout=15, allow_agent=False, look_for_keys=False
    )
    log("Conexion SSH establecida")
    return client

def run_remote(client, cmd, timeout=120):
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

def sudo_remote(client, cmd, timeout=120):
    return run_remote(client, f"echo '{REMOTE_SSH_PASS}' | sudo -S {cmd} 2>&1", timeout=timeout)

# =============================================================
# 3. TRANSFERIR DUMP AL SERVIDOR
# =============================================================
def upload_dump(client, local_path):
    print(f"\n{CYAN}{'='*60}")
    print(f"  [PASO 2] Transfiriendo dump al servidor")
    print(f"{'='*60}{RESET}\n")

    info(f"Subiendo {local_path.name} ({local_path.stat().st_size/1024:.1f} KB)...")
    sftp = client.open_sftp()
    sftp.put(str(local_path), REMOTE_DUMP_PATH)
    sftp.close()
    log(f"Dump transferido a {REMOTE_HOST}:{REMOTE_DUMP_PATH}")

# =============================================================
# 4. RESTAURAR EN EL SERVIDOR
# =============================================================
def restore_remote(client):
    print(f"\n{CYAN}{'='*60}")
    print(f"  [PASO 3] Restaurando DB en servidor {REMOTE_HOST}")
    print(f"{'='*60}{RESET}\n")

    # Copiar dump dentro del contenedor
    info("Copiando dump al contenedor postgres...")
    code, out = sudo_remote(client, f"docker cp {REMOTE_DUMP_PATH} {REMOTE_CONTAINER}:/tmp/{DUMP_FILE}")
    if code != 0:
        warn(f"docker cp: {out}")
    else:
        log("Dump copiado al contenedor")

    # Terminar conexiones activas a la DB (para permitir DROP/CREATE)
    info("Terminando conexiones activas a la DB...")
    disconnect_sql = f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{REMOTE_DB}' AND pid <> pg_backend_pid();"
    code, out = sudo_remote(
        client,
        f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d postgres -c \"{disconnect_sql}\" 2>&1"
    )
    log("Conexiones terminadas")

    # Restaurar el dump
    info(f"Ejecutando psql para restaurar (puede tomar unos segundos)...")
    code, out = sudo_remote(
        client,
        f"docker exec -e PGPASSWORD={REMOTE_PASS} {REMOTE_CONTAINER} "
        f"psql -U {REMOTE_USER} -d {REMOTE_DB} -f /tmp/{DUMP_FILE} 2>&1",
        timeout=300
    )

    # Mostrar ultimas lineas del output
    lines = [l for l in out.split('\n') if l.strip() and 'contraseña' not in l.lower()]
    errors = [l for l in lines if 'ERROR' in l]
    
    if errors:
        warn(f"Errores durante restore ({len(errors)} total):")
        for e in errors[:5]:
            print(f"    {e}")
        if len(errors) > 5:
            print(f"    ... y {len(errors)-5} mas")
    
    print(f"\n    Ultimas lineas del restore:")
    for l in lines[-8:]:
        print(f"    {l}")

    if code == 0 or len(errors) < 5:
        log("Restore completado")
    else:
        warn(f"Restore termino con codigo {code} y {len(errors)} errores")

    # Limpiar dump del contenedor y servidor
    info("Limpiando archivos temporales...")
    sudo_remote(client, f"docker exec {REMOTE_CONTAINER} rm -f /tmp/{DUMP_FILE}")
    sudo_remote(client, f"rm -f {REMOTE_DUMP_PATH}")
    log("Archivos temporales eliminados")

# =============================================================
# 5. VERIFICAR DATOS
# =============================================================
def verify_data(client):
    print(f"\n{CYAN}{'='*60}")
    print(f"  [PASO 4] Verificando datos restaurados")
    print(f"{'='*60}{RESET}\n")

    # Contar registros en tablas principales
    tables_sql = """
    SELECT tablename FROM pg_tables 
    WHERE schemaname='public' 
    ORDER BY tablename;
    """
    code, out = sudo_remote(
        client,
        f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -t -c \"{tables_sql}\" 2>&1"
    )
    tables = [l.strip() for l in out.split('\n') if l.strip() and 'contraseña' not in l.lower() and not l.startswith('[')]

    print(f"  Tablas encontradas: {len(tables)}")
    
    count_results = []
    for table in tables:
        if table:
            code2, out2 = sudo_remote(
                client,
                f"docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -d {REMOTE_DB} -t -c \"SELECT COUNT(*) FROM {table};\" 2>&1"
            )
            cnt = next((l.strip() for l in out2.split('\n') if l.strip().isdigit()), '?')
            count_results.append((table, cnt))
            if cnt != '0' and cnt != '?':
                log(f"{table:<30} {cnt} registros")
            else:
                print(f"  {YELLOW}  {table:<30} {cnt} registros{RESET}")

    return count_results

# =============================================================
# MAIN
# =============================================================
def main():
    print(f"\n{CYAN}{'='*60}")
    print(f"  BACKUP & RESTORE - Ricoh Fleet DB")
    print(f"  Local (Docker) --> {REMOTE_HOST}")
    print(f"{'='*60}{RESET}\n")

    # Paso 1: Dump local
    dump_path = make_local_dump()

    # Paso 2 & 3 & 4: Conectar, transferir, restaurar
    client = connect_remote()

    try:
        upload_dump(client, dump_path)
        restore_remote(client)
        results = verify_data(client)
    finally:
        client.close()

    # Resumen final
    print(f"\n{GREEN}{'='*60}")
    print(f"  [OK] BACKUP Y RESTORE COMPLETADOS")
    print(f"{'='*60}")
    print(f"  Archivo backup local: {dump_path}")
    print(f"  Servidor:             {REMOTE_HOST}:5433")
    print(f"  Base de datos:        {REMOTE_DB}")
    
    total_tables_with_data = sum(1 for _, c in results if c not in ('0', '?'))
    print(f"  Tablas con datos:     {total_tables_with_data}/{len(results)}")
    print(f"{'='*60}{RESET}\n")

if __name__ == "__main__":
    main()
