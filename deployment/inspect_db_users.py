#!/usr/bin/env python3
"""
Inspecciona los usuarios con permisos de escáner en la base de datos de producción.
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
        
        py_code = (
            "from db.database import SessionLocal; "
            "from db.models import Printer; "
            "db = SessionLocal(); "
            "p = db.query(Printer).filter(Printer.ip_address == '192.168.91.251').first(); "
            "print(f'Printer ID: {p.id}, Hostname: {p.hostname}, IP: {p.ip_address}'); "
            "print(f'Location: {p.location}'); "
            "print(f'Admin Password: {p.admin_password}')"
        )
        cmd = f"docker exec -i ricoh-backend python -c \"{py_code}\""
        
        stdin, stdout, stderr = client.exec_command(f"echo '{PASS}' | sudo -S {cmd}")
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        
        # Filtrar prompts
        lines = [l for l in out.split('\n') if '[sudo]' not in l and 'password for' not in l.lower()]
        print("\n--- PRINTER DETAILS ---")
        print('\n'.join(lines))
        if err:
            print("\n--- STDERR ---")
            print(err)
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
