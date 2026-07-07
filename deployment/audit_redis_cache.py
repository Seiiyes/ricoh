import paramiko
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

REDIS_PASS = "aoRJay23ZiakmfggESo5ASkYWG52ohk_lg"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("=== Auditoría de caché Redis para analytics:comparison ===\n")

# Buscar todas las claves de comparison
cmd = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning KEYS 'analytics:comparison*'"
stdin, stdout, stderr = client.exec_command(cmd)
keys = stdout.read().decode('utf-8', errors='replace').strip()
print("Claves de caché 'analytics:comparison*':")
print(keys or "(ninguna encontrada)")

print()

# Contar cuántas claves hay
cmd2 = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning KEYS 'analytics:comparison*' | wc -l"
stdin2, stdout2, stderr2 = client.exec_command(cmd2)
count = stdout2.read().decode('utf-8', errors='replace').strip()
print(f"Total claves de comparison: {count}")

print()

# Verificar TTL de la primera clave
if keys and keys != "(ninguna encontrada)":
    first_key = keys.split('\n')[0].strip().strip('\r')
    if first_key:
        cmd3 = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning TTL '{first_key}'"
        stdin3, stdout3, stderr3 = client.exec_command(cmd3)
        ttl = stdout3.read().decode('utf-8', errors='replace').strip()
        print(f"TTL de '{first_key}': {ttl} segundos")

client.close()
