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

def sudo(cmd, timeout=60):
    return run(f"echo '{PASS}' | sudo -S {cmd} 2>&1", timeout=timeout)

print("=== Abriendo puerto 5432 en el firewall ===\n")

# 1. Verificar estado del firewall
print("[1] Estado del firewall (ufw):")
r = sudo("ufw status")
print(r)

# 2. Abrir puerto 5432
print("\n[2] Abriendo puerto 5432...")
r = sudo("ufw allow 5432/tcp")
print(r)

# 3. Verificar que Docker tambien esta exponiendo el puerto
print("\n[3] Verificando docker port mapping:")
r = sudo("docker port ricoh-postgres")
print(r)

# 4. Si no hay mapping, reiniciar el contenedor con el puerto correcto
if "5432" not in r:
    print("\n[4] Puerto no mapeado - reiniciando postgres con docker compose...")
    r = sudo("docker compose -f /home/odootic/ricoh-app/docker-compose.yml up -d --no-deps postgres 2>&1", timeout=120)
    print(r)
    time.sleep(5)
    r = sudo("docker port ricoh-postgres")
    print(f"Puerto ahora: {r}")
else:
    print("Puerto Docker OK")

# 5. Verificar que postgres escucha en 0.0.0.0
print("\n[5] Verificando que postgres escucha externamente:")
r = sudo("ss -tlnp | grep 5432")
print(r if r else "(no output)")

# 6. Test de conexion local
print("\n[6] Test conexion local con md5:")
r = sudo("docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c 'SELECT version();' 2>&1")
lines = [l for l in r.split('\n') if 'contraseña' not in l.lower() and 'password' not in l.lower()]
print('\n'.join(lines[:5]))

# 7. Mostrar reglas de firewall finales
print("\n[7] Reglas de firewall activas:")
r = sudo("ufw status numbered")
print(r)

client.close()

print("\n=== LISTO ===")
print("Intenta conectar DBeaver con:")
print(f"  Host:     {HOST}")
print(f"  Puerto:   5432")
print(f"  DB:       ricoh_fleet")
print(f"  Usuario:  ricoh_admin")
print(f"  Password: ricoh_secure_2024")
