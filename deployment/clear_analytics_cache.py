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

print("=== Limpiando caché de analytics:comparison en Redis ===\n")

# Eliminar todas las claves de comparison para forzar recalculo con parámetros frescos
cmd = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning KEYS 'analytics:comparison*'"
stdin, stdout, stderr = client.exec_command(cmd)
keys_raw = stdout.read().decode('utf-8', errors='replace').strip()
keys = [k.strip() for k in keys_raw.split('\n') if k.strip() and 'Warning' not in k]

if keys:
    for key in keys:
        del_cmd = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning DEL '{key}'"
        stdin_d, stdout_d, stderr_d = client.exec_command(del_cmd)
        result = stdout_d.read().decode('utf-8', errors='replace').strip()
        print(f"DEL '{key}' -> {result}")
    print(f"\n✅ Eliminadas {len(keys)} claves de comparison.")
else:
    print("No había claves de comparison en caché.")

# También limpiar evolution por si acaso
cmd2 = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning KEYS 'analytics:evolution*'"
stdin2, stdout2, stderr2 = client.exec_command(cmd2)
keys2_raw = stdout2.read().decode('utf-8', errors='replace').strip()
keys2 = [k.strip() for k in keys2_raw.split('\n') if k.strip() and 'Warning' not in k]
if keys2:
    for key in keys2:
        del_cmd2 = f"docker exec ricoh-redis redis-cli -a '{REDIS_PASS}' --no-auth-warning DEL '{key}'"
        stdin_d2, stdout_d2, stderr_d2 = client.exec_command(del_cmd2)
        result2 = stdout_d2.read().decode('utf-8', errors='replace').strip()
        print(f"DEL '{key}' -> {result2}")
    print(f"\n✅ Eliminadas {len(keys2)} claves de evolution.")

client.close()
print("\nCaché de analytics limpiado exitosamente.")
