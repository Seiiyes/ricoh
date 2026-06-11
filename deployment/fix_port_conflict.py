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

def run(cmd, timeout=60):
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

def sudo(cmd, timeout=120):
    return run(f"echo '{PASS}' | sudo -S {cmd} 2>&1", timeout=timeout)

print("=== Cambiando PostgreSQL Docker al puerto 5433 ===\n")

# 1. Ver que ocupa el 5432
print("[1] Puerto 5432 ocupado por:")
r = sudo("ss -tlnp | grep 5432")
print(r)

# 2. Leer docker-compose actual y cambiar 5432 por 5433
print("\n[2] Actualizando docker-compose (5432 -> 5433)...")
r = sudo("sed -i 's/5432:5432/5433:5432/g' /home/odootic/ricoh-app/docker-compose.yml")
print(f"sed: {r if r else 'OK'}")

# Verificar el cambio
r = sudo("grep -A2 'ports:' /home/odootic/ricoh-app/docker-compose.yml | grep 543")
print(f"Puerto en compose: {r}")

# 3. Reiniciar postgres con el nuevo puerto
print("\n[3] Reiniciando contenedor postgres en puerto 5433...")
r = sudo("docker compose -f /home/odootic/ricoh-app/docker-compose.yml up -d --no-deps postgres 2>&1", timeout=60)
print(r)

time.sleep(5)

# 4. Verificar el mapping
print("\n[4] Verificando port mapping Docker:")
r = sudo("docker port ricoh-postgres")
print(r)

# 5. Verificar que 5433 escucha en 0.0.0.0
print("\n[5] Puertos de red activos:")
r = sudo("ss -tlnp | grep 543")
print(r if r else "(ninguno)")

# 6. Test de conexion
print("\n[6] Test conexion al postgres dockerizado:")
r = run("nc -zv 127.0.0.1 5433 2>&1 || echo 'conexion fallida'")
print(r)

client.close()

print("\n=== CONFIGURACION LISTA ===")
print("Conecta en DBeaver con:")
print(f"  Host:     {HOST}")
print(f"  Puerto:   5433  <- NUEVO PUERTO")
print(f"  DB:       ricoh_fleet")
print(f"  Usuario:  ricoh_admin")
print(f"  Password: ricoh_secure_2024")
print(f"  SSH:      NO (conexion directa)")
