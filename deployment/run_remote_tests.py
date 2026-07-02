import paramiko
from pathlib import Path
import sys

# Cargar configuración SSH
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

LOCAL_TEST_PATH = Path(__file__).parent.parent / "backend" / "tests" / "test_secure_session_migration.py"
REMOTE_DIR = f"/home/{USER}/ricoh-app"
REMOTE_TEST_PATH = f"{REMOTE_DIR}/backend/tests/test_secure_session_migration.py"

print(f"Connecting to remote server: {HOST}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

# 1. Subir archivo de pruebas
print(f"Uploading {LOCAL_TEST_PATH.name} to server...")
sftp = client.open_sftp()
sftp.put(str(LOCAL_TEST_PATH), REMOTE_TEST_PATH)
sftp.close()

# 2. Ejecutar pruebas como script de Python dentro del contenedor docker backend
print("Running standalone tests inside 'ricoh-backend' container...")
cmd = "docker exec ricoh-backend python tests/test_secure_session_migration.py"
stdin, stdout, stderr = client.exec_command(cmd)

out = stdout.read().decode('utf-8', errors='replace')
err = stderr.read().decode('utf-8', errors='replace')

print("\n=== TEST OUTPUT ===")
print(out)

if err:
    print("\n=== TEST ERROR ===")
    print(err)

# 3. Limpiar archivo de pruebas en el servidor
print("Cleaning up remote test file...")
client.exec_command(f"rm {REMOTE_TEST_PATH}")

client.close()
print("Execution completed.")
