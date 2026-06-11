#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
deploy_to_server131.py
======================
Script de despliegue completo para el servidor 192.168.91.131
usando paramiko (SSH) y SFTP.

Uso:
    python deployment/deploy_to_server131.py

Requiere:
    pip install paramiko
"""

import os
import time
import paramiko
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config

SERVER_IP, USERNAME, PASSWORD = load_ssh_config()
SSH_PORT    = 22
REMOTE_DIR  = f"/home/{USERNAME}/ricoh-app"
LOCAL_DIR   = Path(__file__).parent.parent  # raiz del proyecto

EXCLUDE_DIRS = {
    "__pycache__", ".pytest_cache", "venv", ".env",
    "node_modules", ".git", ".hypothesis", "dist",
    ".vscode", ".kiro", "backups", "backup"
}
EXCLUDE_FILES = {".pyc", ".pyo", ".log"}

# =============================================================================
# COLORES
# =============================================================================
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

def log(msg):   print(f"{GREEN}  [OK] {msg}{RESET}", flush=True)
def warn(msg):  print(f"{YELLOW}  [!]  {msg}{RESET}", flush=True)
def error(msg): print(f"{RED}  [ERR] {msg}{RESET}", flush=True); sys.exit(1)
def info(msg):  print(f"{CYAN}  -->  {msg}{RESET}", flush=True)

def banner():
    print(f"\n{CYAN}{'='*60}")
    print(f"  [RICOH] Ricoh Equipment Management Suite")
    print(f"  Despliegue -> {SERVER_IP}")
    print(f"{'='*60}{RESET}\n", flush=True)

# =============================================================================
# CONEXION SSH
# =============================================================================
def connect_ssh():
    info(f"Conectando a {USERNAME}@{SERVER_IP}:{SSH_PORT}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SERVER_IP,
        port=SSH_PORT,
        username=USERNAME,
        password=PASSWORD,
        timeout=30,
        allow_agent=False,
        look_for_keys=False
    )
    log(f"Conexion SSH establecida")
    return client

# =============================================================================
# EJECUTAR COMANDO REMOTO - STREAMING
# Usa "echo pass | sudo -S" para evitar prompts interactivos de sudo
# =============================================================================
def run_cmd(client, cmd, timeout=600, show_output=True, use_sudo=False):
    """
    Ejecuta un comando SSH con lectura en streaming.
    Si use_sudo=True, prefija con 'echo PASSWORD | sudo -S'.
    """
    if use_sudo:
        # Envolver en sh -c para que sudo -S lea de stdin
        full_cmd = f"echo '{PASSWORD}' | sudo -S sh -c '{cmd.replace(chr(39), chr(34))}'"
    else:
        full_cmd = cmd

    channel = client.get_transport().open_session()
    channel.set_combine_stderr(True)
    channel.exec_command(full_cmd)

    output_lines = []
    deadline = time.time() + timeout

    while True:
        if channel.recv_ready():
            data = channel.recv(4096).decode("utf-8", errors="replace")
            for line in data.splitlines():
                output_lines.append(line)
                if show_output and line.strip():
                    print(f"    {line}", flush=True)

        if channel.exit_status_ready() and not channel.recv_ready():
            break

        if time.time() > deadline:
            warn(f"Timeout ({timeout}s) en comando: {cmd[:70]}...")
            channel.close()
            return -1, "\n".join(output_lines)

        time.sleep(0.1)

    # Leer lo que quede
    remaining = channel.recv(65535)
    if remaining:
        data = remaining.decode("utf-8", errors="replace")
        for line in data.splitlines():
            output_lines.append(line)
            if show_output and line.strip():
                print(f"    {line}", flush=True)

    exit_code = channel.recv_exit_status()
    channel.close()
    return exit_code, "\n".join(output_lines)

def run_sudo(client, cmd, timeout=600, show_output=True):
    """Atajo para ejecutar con sudo."""
    return run_cmd(client, cmd, timeout=timeout, show_output=show_output, use_sudo=True)

# =============================================================================
# TRANSFERENCIA SFTP
# =============================================================================
def should_exclude(path_str):
    for part in Path(path_str).parts:
        if part in EXCLUDE_DIRS:
            return True
    return Path(path_str).suffix in EXCLUDE_FILES

def sftp_mkdirs(sftp, remote_path):
    dirs = []
    path = remote_path
    while path and path != "/":
        try:
            sftp.stat(path)
            break
        except FileNotFoundError:
            dirs.append(path)
            path = os.path.dirname(path)
    for d in reversed(dirs):
        try:
            sftp.mkdir(d)
        except Exception:
            pass

def upload_dir(sftp, local_dir, remote_dir, label=""):
    local = Path(local_dir)
    if not local.exists():
        warn(f"No existe localmente: {local}")
        return 0, 0
    count, errs = 0, 0
    for item in local.rglob("*"):
        rel = item.relative_to(local)
        if should_exclude(str(rel)):
            continue
        rpath = f"{remote_dir}/{rel.as_posix()}"
        if item.is_dir():
            sftp_mkdirs(sftp, rpath)
        elif item.is_file():
            try:
                sftp_mkdirs(sftp, os.path.dirname(rpath))
                sftp.put(str(item), rpath)
                count += 1
                if count % 30 == 0:
                    print(f"    [{label}] {count} archivos...", flush=True)
            except Exception as ex:
                warn(f"Error subiendo {rel}: {ex}")
                errs += 1
    return count, errs

def upload_file(sftp, src, dst):
    sftp_mkdirs(sftp, os.path.dirname(dst))
    sftp.put(str(src), dst)

# =============================================================================
# INSTALAR DOCKER
# =============================================================================
def ensure_docker(client):
    info("Verificando Docker...")
    code, out = run_cmd(client, "docker --version 2>/dev/null || echo NO_DOCKER", timeout=15, show_output=False)
    if "NO_DOCKER" in out or code != 0:
        warn("Docker no instalado. Instalando (2-5 min)...")
        # Actualizar apt e instalar dependencias
        run_sudo(client, "apt-get update -qq", timeout=120, show_output=False)
        run_sudo(client, "apt-get install -y -qq curl ca-certificates", timeout=120, show_output=False)
        # Instalar Docker via script oficial
        code2, out2 = run_cmd(
            client,
            f"curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && echo '{PASSWORD}' | sudo -S sh /tmp/get-docker.sh",
            timeout=600,
            show_output=True
        )
        if code2 == 0:
            run_sudo(client, f"usermod -aG docker {USERNAME}", timeout=30, show_output=False)
            run_sudo(client, "systemctl enable docker && systemctl start docker", timeout=60, show_output=False)
            log("Docker instalado")
        else:
            warn("Instalacion de Docker pudo haber fallado - continuando...")
    else:
        docker_ver = next((l for l in out.split("\n") if "Docker" in l), out.strip()[:60])
        log(f"Docker: {docker_ver.strip()}")

    # Asegurar docker compose plugin
    code3, out3 = run_cmd(client, "docker compose version 2>/dev/null || echo NO_COMPOSE", timeout=15, show_output=False)
    if "NO_COMPOSE" in out3:
        warn("Instalando Docker Compose plugin...")
        run_sudo(client, "apt-get install -y -qq docker-compose-plugin", timeout=300, show_output=False)
        log("Docker Compose plugin instalado")
    else:
        log("Docker Compose disponible")

# =============================================================================
# MAIN
# =============================================================================
def main():
    banner()

    # 1. Conectar
    client = connect_ssh()

    # 2. Instalar Docker si falta
    ensure_docker(client)

    # 3. Preparar directorio
    info(f"Preparando directorio: {REMOTE_DIR}")
    run_cmd(client, f"mkdir -p {REMOTE_DIR}", timeout=15, show_output=False)
    log("Directorio listo")

    # 4. Detener contenedores previos
    info("Limpiando contenedores anteriores...")
    run_sudo(client, f"docker compose -f {REMOTE_DIR}/docker-compose.yml down --remove-orphans 2>/dev/null || true", timeout=60, show_output=False)

    # 5. Transferir archivos via SFTP
    print(f"\n{CYAN}  Transfiriendo archivos...{RESET}", flush=True)
    sftp = client.open_sftp()

    info("Subiendo backend (FastAPI)...")
    c, e = upload_dir(sftp, LOCAL_DIR / "backend", f"{REMOTE_DIR}/backend", "backend")
    log(f"Backend: {c} archivos ({e} errores)")

    info("Subiendo src (React frontend)...")
    c, e = upload_dir(sftp, LOCAL_DIR / "src", f"{REMOTE_DIR}/src", "src")
    log(f"Frontend: {c} archivos ({e} errores)")

    if (LOCAL_DIR / "public").exists():
        info("Subiendo public...")
        c, e = upload_dir(sftp, LOCAL_DIR / "public", f"{REMOTE_DIR}/public", "public")
        log(f"Public: {c} archivos ({e} errores)")

    info("Subiendo archivos raiz...")
    for f in ["package.json", "vite.config.ts", "tsconfig.json",
              "tsconfig.app.json", "index.html", "postcss.config.js",
              "eslint.config.js", "tsconfig.node.json"]:
        src = LOCAL_DIR / f
        if src.exists():
            try:
                upload_file(sftp, src, f"{REMOTE_DIR}/{f}")
            except Exception as ex:
                warn(f"Error subiendo {f}: {ex}")
    log("Archivos raiz listos")

    info("Subiendo docker-compose.yml...")
    dc_src = LOCAL_DIR / "deployment" / "docker-compose.server131.yml"
    if not dc_src.exists():
        error(f"No se encontro: {dc_src}")
    upload_file(sftp, dc_src, f"{REMOTE_DIR}/docker-compose.yml")
    sftp.close()
    log("Transferencia completa")

    # 6. Docker Compose up --build
    print(f"\n{CYAN}  Construyendo e iniciando servicios...{RESET}", flush=True)
    info("docker compose up --build -d (puede tardar 5-15 min la primera vez)")

    code, out = run_sudo(
        client,
        f"docker compose -f {REMOTE_DIR}/docker-compose.yml up --build -d 2>&1",
        timeout=900
    )
    if code == 0:
        log("Servicios iniciados correctamente")
    else:
        warn(f"docker compose termino con codigo {code}")

    # 7. Verificar estado
    info("Esperando 45 segundos para que los servicios arranquen...")
    time.sleep(45)

    print(f"\n{CYAN}  Estado de contenedores:{RESET}", flush=True)
    run_sudo(client, f"docker compose -f {REMOTE_DIR}/docker-compose.yml ps 2>&1", timeout=30)

    # 8. Health check
    info("Verificando backend API...")
    ok = False
    for i in range(1, 7):
        code, out = run_cmd(
            client,
            "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health 2>/dev/null || echo 000",
            timeout=15,
            show_output=False
        )
        http = out.strip().split("\n")[-1].strip()
        if http in ("200", "404", "422"):
            log(f"Backend API responde (HTTP {http})")
            ok = True
            break
        warn(f"Backend no disponible aun (intento {i}/6, cod: {http}). Esperando 15s...")
        time.sleep(15)

    if not ok:
        warn("Backend no respondio. Mostrando logs:")
        run_sudo(client, f"docker compose -f {REMOTE_DIR}/docker-compose.yml logs --tail=40 backend 2>&1", timeout=30)

    client.close()

    # 9. Resumen
    print(f"\n{GREEN}{'='*60}")
    print(f"  [OK] DESPLIEGUE COMPLETADO")
    print(f"{'='*60}")
    print(f"  Frontend:  http://{SERVER_IP}")
    print(f"  Backend:   http://{SERVER_IP}:8000")
    print(f"  API Docs:  http://{SERVER_IP}:8000/docs")
    print(f"\n  En el servidor:")
    print(f"  ssh {USERNAME}@{SERVER_IP}")
    print(f"  cd ~/ricoh-app && sudo docker compose logs -f")
    print(f"{'='*60}{RESET}\n", flush=True)

if __name__ == "__main__":
    main()
