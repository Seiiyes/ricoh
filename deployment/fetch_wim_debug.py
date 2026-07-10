#!/usr/bin/env python3
"""
Descarga los archivos HTML de diagnóstico desde el servidor
que fueron guardados durante el último intento de delete.
"""
import paramiko
import sys
import os
import io

sys.path.insert(0, os.path.dirname(__file__))
from ssh_config import load_ssh_config

HOST, USER, PASS = load_ssh_config()
LOCAL_DIR = "C:/Users/juan.lizarazo/Desktop/ricoh"

print(f"Conectando a {HOST}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15,
               allow_agent=False, look_for_keys=False)

sftp = client.open_sftp()

# Buscar archivos de diagnóstico en /tmp
def run(cmd):
    _, stdout, _ = client.exec_command(cmd)
    return stdout.read().decode('utf-8', errors='replace').strip()

files = run("ls /tmp/wim_*.html 2>/dev/null").split('\n')
print(f"\nArchivos encontrados en /tmp: {files}")

for remote_path in files:
    remote_path = remote_path.strip()
    if not remote_path:
        continue
    fname = os.path.basename(remote_path)
    local_path = f"{LOCAL_DIR}/server_{fname}"
    try:
        sftp.get(remote_path, local_path)
        size = os.path.getsize(local_path)
        print(f"  Descargado: {fname}  ({size} bytes)")
    except Exception as e:
        print(f"  Error descargando {fname}: {e}")

sftp.close()

# Mostrar los logs relevantes del backend
print("\n--- Logs recientes del backend (delete job) ---")
logs = run("docker logs ricoh-backend --tail=200 2>&1 | grep -E 'delete|job|typeOnly|ALL form|payload|POST response|Still|PRESENT|DELETED' | tail -40")
print(logs.encode('ascii', errors='replace').decode())


client.close()
print("\nListo.")
