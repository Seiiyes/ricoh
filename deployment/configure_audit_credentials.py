#!/usr/bin/env python3
"""
Script utilitario para configurar las credenciales de auditoría (AUDIT_USERS)
directamente en el archivo .env del servidor remoto de producción por SSH.
(ASCII safe version to prevent encoding issues on Windows)
"""
import paramiko
import sys
from pathlib import Path

# Cargar configuración SSH local
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

REMOTE_ENV_PATH = f"/home/{USER}/ricoh-app/.env"


def run_remote_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err


def main():
    print("="*60)
    print(f"CONNECTING TO {HOST} TO CONFIGURE AUDIT CREDENTIALS")
    print("="*60)
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)
        print("[OK] SSH Connection established.")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return

    # 1. Generar hash bcrypt de la contraseña localmente en Windows
    print("\n[GENERATING BCRYPT HASH LOCALLY]")
    try:
        import bcrypt
        password_bytes = "ricohLogs2026".encode('utf-8')
        salt = bcrypt.gensalt()
        bcrypt_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        print(f"[OK] Generated Bcrypt Hash: {bcrypt_hash}")
    except Exception as local_e:
        print(f"[ERROR] Failed to generate hash locally: {local_e}")
        client.close()
        return

    # 2. Leer el .env remoto
    print("\n[READING REMOTE .env]")
    sftp = client.open_sftp()
    try:
        with sftp.open(REMOTE_ENV_PATH, "r") as f:
            env_content = f.read().decode('utf-8', errors='replace')
        print("[OK] .env file loaded successfully.")
    except FileNotFoundError:
        env_content = ""
        print("[WARNING] .env file not found. Creating a new one.")

    # 3. Actualizar la variable AUDIT_USERS
    escaped_hash = bcrypt_hash.replace('$', '$$')
    audit_users_var = f'AUDIT_USERS="admin_audit:{escaped_hash}"'
    lines = env_content.split('\n')
    updated_lines = []
    found = False
    
    for line in lines:
        if line.startswith('AUDIT_USERS='):
            updated_lines.append(audit_users_var)
            found = True
        else:
            updated_lines.append(line)
            
    if not found:
        # Añadir al final si no existe
        if updated_lines and updated_lines[-1] != "":
            updated_lines.append("")
        updated_lines.append(audit_users_var)

    new_env_content = '\n'.join(updated_lines)

    # 4. Guardar el .env remoto
    with sftp.open(REMOTE_ENV_PATH, "w") as f:
        f.write(new_env_content.encode('utf-8'))
    print("[OK] .env file updated remotely.")
    sftp.close()

    # 5. Reiniciar contenedores en producción para aplicar cambios
    print("\n[REAPPLYING DOCKER CONFIGURATION]")
    cmd_restart = f"echo '{PASS}' | sudo -S docker compose -f /home/{USER}/ricoh-app/docker-compose.yml up -d"
    out_restart, err_restart = run_remote_cmd(client, cmd_restart)
    print("[OK] Containers restarted with new variables.")
    print("------------------------------------------------------------")
    print(f"Portal de Auditoria listo en: http://{HOST}:8088")
    print("Credenciales por defecto configuradas:")
    print(" - Usuario: admin_audit")
    print(" - Contrasena: ricohLogs2026")
    print("------------------------------------------------------------")
    
    client.close()


if __name__ == "__main__":
    main()
