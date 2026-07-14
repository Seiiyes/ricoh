#!/usr/bin/env python3
import paramiko
import os
import sys
from pathlib import Path

# Cargar configuración SSH
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config

HOST, USER, PASS = load_ssh_config()

LOCAL_DOCS_DIR = Path(__file__).parent.parent / "docs"
REMOTE_DOCS_DIR = f"/home/{USER}/ricoh-app/docs"

print("="*60)
print(f"UPLOADING DOCS TO PRODUCTION SERVER: {HOST}")
print("="*60)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)

sftp = client.open_sftp()

def recreate_remote_dir(sftp, remote_path):
    """Crea directorios remotos de forma recursiva si no existen"""
    parts = remote_path.replace('\\', '/').split('/')
    current = ""
    for part in parts:
        if not part:
            continue
        if current == "" and remote_path.startswith('/'):
            current = "/" + part
        else:
            current += "/" + part
        try:
            sftp.mkdir(current)
        except IOError:
            pass

def upload_directory_recursive(sftp, local_dir, remote_dir):
    """Sube una carpeta local de forma recursiva al servidor remoto"""
    recreate_remote_dir(sftp, remote_dir)
    for entry in os.scandir(local_dir):
        if entry.is_dir():
            # Evitar subir carpetas ocultas de git o editor
            if entry.name.startswith('.'):
                continue
            upload_directory_recursive(sftp, entry.path, f"{remote_dir}/{entry.name}")
        elif entry.is_file():
            # Evitar subir archivos temporales u ocultos
            if entry.name.startswith('.'):
                continue
            local_file = entry.path
            remote_file = f"{remote_dir}/{entry.name}"
            print(f"Uploading {local_file} -> {remote_file}")
            sftp.put(local_file, remote_file)

# Iniciar carga recursiva
upload_directory_recursive(sftp, str(LOCAL_DOCS_DIR), REMOTE_DOCS_DIR)

sftp.close()
client.close()

print("="*60)
print("DOCS FOLDER UPLOADED SUCCESSFULLY TO THE SERVER.")
print("="*60)
