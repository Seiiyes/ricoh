#!/usr/bin/env python3
import paramiko, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, allow_agent=False, look_for_keys=False)

def run(cmd, timeout=30):
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
    return out.decode('utf-8', errors='replace').strip()

def sudo(cmd, timeout=30):
    return run(f"echo '{PASS}' | sudo -S {cmd} 2>&1", timeout=timeout)

print("=== Configurando PostgreSQL para acceso externo ===\n")

# 1. Exponer puerto 5432 en docker-compose
print("[1] Exponiendo puerto 5432 en la red local...")
r = sudo("sed -i '/container_name: ricoh-postgres/a\\    ports:\\n      - \"5432:5432\"' /home/odootic/ricoh-app/docker-compose.yml 2>&1")

# Mejor: modificar el archivo directamente
# Verificar si ya tiene ports
check = sudo("grep -A5 'container_name: ricoh-postgres' /home/odootic/ricoh-app/docker-compose.yml")
print(f"Estado actual postgres:\n{check}\n")

# 2. Cambiar autenticacion a md5 en pg_hba.conf dentro del contenedor
print("[2] Cambiando autenticacion a md5...")
r = sudo("docker exec ricoh-postgres bash -c \"sed -i 's/scram-sha-256/md5/g' /var/lib/postgresql/data/pgdata/pg_hba.conf\"")
print(f"sed result: {r}")

# 3. Verificar el cambio
r = sudo("docker exec ricoh-postgres cat /var/lib/postgresql/data/pgdata/pg_hba.conf")
print(f"\npg_hba.conf actual:\n{r}\n")

# 4. Recargar configuracion de postgres (sin reiniciar)
print("[3] Recargando configuracion de PostgreSQL...")
r = sudo("docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c 'SELECT pg_reload_conf();'")
print(f"Reload: {r}")

# 5. Exponer puerto 5432 al host
print("\n[4] Actualizando docker-compose para exponer puerto 5432...")
# Leer el archivo actual
compose = sudo("cat /home/odootic/ricoh-app/docker-compose.yml")
if "5432:5432" in compose:
    print("Puerto 5432 ya esta expuesto")
else:
    # Agregar ports al servicio postgres usando python en el servidor
    py_script = """
import yaml
with open('/home/odootic/ricoh-app/docker-compose.yml', 'r') as f:
    data = yaml.safe_load(f)
if 'ports' not in data['services']['postgres']:
    data['services']['postgres']['ports'] = ['5432:5432']
with open('/home/odootic/ricoh-app/docker-compose.yml', 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
print('OK: puerto 5432 agregado')
"""
    r = sudo(f"python3 -c \"{py_script}\"")
    print(f"Result: {r}")

    # Reiniciar solo postgres para aplicar el puerto
    print("\n[5] Reiniciando postgres con nuevo puerto...")
    r = sudo("docker compose -f /home/odootic/ricoh-app/docker-compose.yml up -d --no-deps postgres 2>&1", timeout=60)
    print(r)

# 6. Verificar conectividad
print("\n[6] Verificando conexion con md5...")
r = sudo("docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c '\\l' 2>&1")
print(r)

client.close()

print("\n=== CONFIGURACION COMPLETADA ===")
print(f"Ahora en DBeaver conecta con:")
print(f"  Host:     {HOST}")
print(f"  Puerto:   5432")
print(f"  DB:       ricoh_fleet")
print(f"  Usuario:  ricoh_admin")
print(f"  Password: ricoh_secure_2024")
print(f"  Auth:     MD5 (sin SSH tunnel necesario)")
