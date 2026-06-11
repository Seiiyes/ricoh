#!/usr/bin/env python3
import paramiko, time, sys, io, os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

GREEN  = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"; CYAN = "\033[96m"; RESET = "\033[0m"
def log(m):  print(f"{GREEN}  [OK] {m}{RESET}", flush=True)
def warn(m): print(f"{YELLOW}  [!]  {m}{RESET}", flush=True)
def err(m):  print(f"{RED}  [ERR] {m}{RESET}", flush=True); sys.exit(1)
def info(m): print(f"{CYAN}  -->  {m}{RESET}", flush=True)

# Conectar SSH
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
info(f"Conectando a {USER}@{HOST}...")
client.connect(HOST, username=USER, password=PASS, timeout=15)
log("Conexión SSH establecida")

def run(cmd, timeout=300):
    ch = client.get_transport().open_session()
    ch.set_combine_stderr(True)
    escaped_cmd = cmd.replace("'", "'\\''")
    ch.exec_command(f"echo '{PASS}' | sudo -S bash -c '{escaped_cmd}' 2>&1")
    out = b''
    deadline = time.time() + timeout
    while True:
        if ch.recv_ready(): out += ch.recv(4096)
        if ch.exit_status_ready() and not ch.recv_ready(): break
        if time.time() > deadline: break
        time.sleep(0.1)
    out += ch.recv(65535)
    ch.close()
    lines = [l for l in out.decode('utf-8', errors='replace').split('\n') if '[sudo]' not in l and 'password for' not in l.lower()]
    return ch.recv_exit_status(), '\n'.join(lines).strip()

# 1. Detener contenedores actuales si existen
print(f"\n{CYAN}{'='*60}")
print("  [PASO 1] Deteniendo contenedores actuales...")
print(f"{'='*60}{RESET}\n")
code, out = run("docker compose -f /home/odootic/ricoh-app/docker-compose.yml down")
print(out)
log("Contenedores detenidos")

# 2. Hacer backup del directorio ricoh-app actual
print(f"\n{CYAN}{'='*60}")
print("  [PASO 2] Respaldando carpeta ricoh-app...")
print(f"{'='*60}{RESET}\n")
backup_dir = f"/home/odootic/ricoh-app-backup-{int(time.time())}"
code, out = run(f"mv /home/odootic/ricoh-app {backup_dir}")
if code == 0:
    log(f"Carpeta antigua renombrada a: {backup_dir}")
else:
    warn(f"No se pudo renombrar (posiblemente no existía): {out}")

# 3. Clonar repositorio público de GitHub
print(f"\n{CYAN}{'='*60}")
print("  [PASO 3] Clonando repositorio público de GitHub...")
print(f"{'='*60}{RESET}\n")
code, out = run("git clone https://github.com/Seiiyes/ricoh /home/odootic/ricoh-app")
print(out)
if code != 0:
    err("Error al clonar el repositorio de GitHub")
run("chown -R odootic:odootic /home/odootic/ricoh-app")
log("Repositorio clonado exitosamente en el servidor")

# 4. Configurar docker-compose.yml para producción (Servidor 131)
print(f"\n{CYAN}{'='*60}")
print("  [PASO 4] Configurando docker-compose.yml en servidor...")
print(f"{'='*60}{RESET}\n")
code, out = run("cp /home/odootic/ricoh-app/deployment/docker-compose.server131.yml /home/odootic/ricoh-app/docker-compose.yml")
if code != 0:
    err(f"No se pudo copiar el archivo docker-compose: {out}")
log("docker-compose.yml copiado y listo")

# 5. Crear script de actualización automatizado en el servidor
print(f"\n{CYAN}{'='*60}")
print("  [PASO 5] Creando script 'update.sh' en el servidor...")
print(f"{'='*60}{RESET}\n")

update_script = """#!/bin/bash
set -e
echo "========================================="
echo "📥 Descargando actualizaciones de Git..."
echo "========================================="
git pull

echo "⚙️  Configurando docker-compose..."
cp deployment/docker-compose.server131.yml docker-compose.yml

echo "🐳 Reconstruyendo e iniciando contenedores..."
docker compose up --build -d

echo "========================================="
echo "✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO"
echo "========================================="
"""

# Escribir el script en el servidor
sftp = client.open_sftp()
remote_script_path = "/home/odootic/ricoh-app/update.sh"
with sftp.open(remote_script_path, "w") as f:
    f.write(update_script)
sftp.close()

# Dar permisos de ejecución
code, out = run("chmod +x /home/odootic/ricoh-app/update.sh")
log("Script 'update.sh' creado y con permisos de ejecución")

# 6. Levantar contenedores clonados de Git
print(f"\n{CYAN}{'='*60}")
print("  [PASO 6] Iniciando contenedores desde la versión de Git...")
print(f"{'='*60}{RESET}\n")
code, out = run("cd /home/odootic/ricoh-app && docker compose up --build -d")
print(out)
if code != 0:
    err("Error al iniciar los servicios")
log("Servicios iniciados correctamente")

# 7. Verificar estado final
print(f"\n{CYAN}{'='*60}")
print("  [PASO 7] Estado de los contenedores...")
print(f"{'='*60}{RESET}\n")
code, out = run("docker ps")
print(out)

client.close()

print(f"\n{GREEN}{'='*60}")
print("🎉 SERVIDOR INTEGRADO CON GIT EXITOSAMENTE")
print(f"{'='*60}")
print("  El servidor ahora corre la versión clonada de GitHub.")
print("  Para actualizar el servidor en el futuro, solo debes:")
print("    1. Conectarte por SSH:")
print(f"       ssh {USER}@{HOST}")
print("    2. Ejecutar el comando:")
print("       cd ~/ricoh-app && ./update.sh")
print(f"{'='*60}{RESET}\n")
