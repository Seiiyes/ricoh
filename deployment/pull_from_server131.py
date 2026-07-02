#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import os
import stat
import time
from pathlib import Path
import paramiko

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

def log(msg):   print(f"{GREEN}  [OK] {msg}{RESET}", flush=True)
def warn(msg):  print(f"{YELLOW}  [!]  {msg}{RESET}", flush=True)
def error(msg): print(f"{RED}  [ERR] {msg}{RESET}", flush=True); sys.exit(1)
def info(msg):  print(f"{CYAN}  -->  {msg}{RESET}", flush=True)

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
    log("Conexión SSH establecida para descarga")
    return client

def should_exclude(rel_path_str):
    parts = Path(rel_path_str).parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    return Path(rel_path_str).suffix in EXCLUDE_FILES

def download_file_sftp(sftp, remote_file, local_file):
    local_path = Path(local_file)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if we should download (based on modification time or size)
    try:
        remote_stat = sftp.stat(remote_file)
        remote_mtime = remote_stat.st_mtime
        remote_size = remote_stat.st_size
        
        if local_path.exists():
            local_stat = local_path.stat()
            # If local is newer or equal and has same size, skip
            if local_stat.st_mtime >= remote_mtime and local_stat.st_size == remote_size:
                return False
    except Exception:
        pass # If error getting remote stat, download anyway
        
    sftp.get(remote_file, str(local_file))
    # Update local modified time to match remote
    try:
        os.utime(str(local_file), (remote_mtime, remote_mtime))
    except Exception:
        pass
    return True

def sync_remote_to_local(sftp, remote_dir, local_dir):
    downloaded_count = 0
    skipped_count = 0
    error_count = 0
    
    # Stack for DFS traversal
    dirs_to_process = [remote_dir]
    
    while dirs_to_process:
        curr_remote = dirs_to_process.pop()
        try:
            entries = sftp.listdir_attr(curr_remote)
        except Exception as e:
            warn(f"Error listando {curr_remote}: {e}")
            error_count += 1
            continue
            
        for entry in entries:
            name = entry.filename
            rpath = f"{curr_remote}/{name}"
            
            # Get relative path from REMOTE_DIR
            rel_path = rpath[len(REMOTE_DIR)+1:]
            
            if should_exclude(rel_path):
                continue
                
            lpath = LOCAL_DIR / rel_path
            
            if stat.S_ISDIR(entry.st_mode):
                dirs_to_process.append(rpath)
            else:
                try:
                    if download_file_sftp(sftp, rpath, lpath):
                        downloaded_count += 1
                        print(f"    [DESCARGADO] {rel_path}", flush=True)
                    else:
                        skipped_count += 1
                except Exception as ex:
                    warn(f"Error descargando {rel_path}: {ex}")
                    error_count += 1
                    
    return downloaded_count, skipped_count, error_count

def main():
    print(f"\n{CYAN}{'='*60}")
    print(f"  [RICOH] Ricoh Equipment Management Suite")
    print(f"  Sincronizar REMOTO -> LOCAL ({SERVER_IP})")
    print(f"{'='*60}{RESET}\n", flush=True)
    
    client = connect_ssh()
    sftp = client.open_sftp()
    
    info("Escaneando y descargando cambios desde el servidor...")
    downloaded, skipped, errors = sync_remote_to_local(sftp, REMOTE_DIR, LOCAL_DIR)
    
    sftp.close()
    client.close()
    
    print(f"\n{GREEN}{'='*60}")
    print("  [OK] SINCRONIZACIÓN COMPLETADA")
    print(f"{'='*60}")
    print(f"  Archivos descargados (nuevos/modificados): {downloaded}")
    print(f"  Archivos al día (omitidos):               {skipped}")
    print(f"  Errores de descarga:                      {errors}")
    print(f"{'='*60}{RESET}\n", flush=True)

if __name__ == "__main__":
    main()
