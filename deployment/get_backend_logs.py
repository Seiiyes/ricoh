#!/usr/bin/env python3
"""
Script utilitario para obtener los logs de docker del contenedor ricoh-backend.
"""
import paramiko
import sys
import io
from pathlib import Path

# Configurar encoding a UTF-8 para consola de Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Cargar configuración SSH local
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)
        stdin, stdout, stderr = client.exec_command("docker logs --tail 50 ricoh-backend")
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        print("--- STDOUT ---")
        print(out)
        print("--- STDERR ---")
        print(err)
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
