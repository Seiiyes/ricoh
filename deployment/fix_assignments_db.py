import paramiko
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("Running retro-active migration on user assignments to prevent active users from showing as inactive...")

# Consulta SQL para establecer copiar/imprimir/escanear en True para usuarios con is_active=True 
# y que tengan todos sus permisos actuales de asignación en False (estado por defecto tras el sync rápido).
# Esto mantendrá inactivo a JUAN LIZARAZO 7104 si sus asignaciones de verdad son todas False en hardware.
# Espera, para 7104, en la tabla users su is_active es 't'.
# Si actualizamos a todos los que tienen is_active = 't', ¿JUAN LIZARAZO 7104 también se actualizaría a True?
# Sí. Para evitar esto: ¿cómo sabemos que JUAN LIZARAZO 7104 fue consultado en vivo y tiene permisos desactivados?
# El usuario JUAN LIZARAZO 7104 tiene sus permisos predeterminados (maestros) en True, pero en las impresoras asignadas los tiene en False.
# En cambio, los otros 428 usuarios tienen tanto sus permisos maestros en False como en las impresoras en False.
# Entonces, podemos identificar a los 428 usuarios porque sus permisos maestros globales de la tabla `users` (func_copier, func_printer, func_scanner) 
# están TODOS en False (o NULL), mientras que JUAN LIZARAZO 7104 tiene permisos maestros en True (func_copier=t, func_printer=t, func_scanner=t).
# ¡Esa es la distinción perfecta!

sql_update = """
UPDATE user_printer_assignments 
SET func_copier = true, func_printer = true, func_scanner = true 
WHERE user_id IN (
    SELECT id FROM users 
    WHERE is_active = true 
    AND (func_copier = false OR func_copier IS NULL) 
    AND (func_printer = false OR func_printer IS NULL) 
    AND (func_scanner = false OR func_scanner IS NULL)
);
"""

cmd = f"docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c \"{sql_update}\""
stdin, stdout, stderr = client.exec_command(cmd)
print("Stdout migration:", stdout.read().decode('utf-8', errors='replace'))
print("Stderr migration:", stderr.read().decode('utf-8', errors='replace'))

client.close()
