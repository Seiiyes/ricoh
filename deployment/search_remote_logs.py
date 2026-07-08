#!/usr/bin/env python3
"""
Script utilitario para buscar logs relacionados con una IP de impresora específica
en los archivos de logs del contenedor de backend remoto.
"""
import paramiko
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()


def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)
        print("[OK] SSH Connection established.")
        
        # Buscar en docker logs históricos
        cmd = "docker logs ricoh-backend 2>&1 | grep 'ricoh_password_flow' | tail -n 80"
        stdin, stdout, stderr = client.exec_command(f"echo '{PASS}' | sudo -S {cmd}")
        out = stdout.read().decode('utf-8', errors='replace').strip()
        
        # Filtrar prompts de sudo
        lines = [l for l in out.split('\n') if '[sudo]' not in l and 'password for' not in l.lower()]
        print("\n--- DOCKER LOGS RECIENTES (192.168.91.251 / 7104) ---")
        if lines and lines[0]:
            print('\n'.join(lines))
        else:
            print("No se encontraron logs específicos en la última ventana de 15 minutos.")
            
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
