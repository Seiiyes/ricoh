#!/usr/bin/env python3
"""
Lee e imprime las variables del archivo .env remoto.
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
        
        sftp = client.open_sftp()
        with sftp.open(f"/home/{USER}/ricoh-app/.env", "r") as f:
            content = f.read().decode('utf-8', errors='replace')
        print(content)
        sftp.close()
        client.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
