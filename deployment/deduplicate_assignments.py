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

print("Starting deduplication of user_printer_assignments in production database...")

# Consulta SQL para eliminar duplicados manteniendo el ID más alto de asignación por cada par (user_id, printer_id)
sql_dedup = """
DELETE FROM user_printer_assignments a 
WHERE a.id < (
    SELECT MAX(b.id) 
    FROM user_printer_assignments b 
    WHERE a.user_id = b.user_id 
    AND a.printer_id = b.printer_id
);
"""

cmd = f"docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c \"{sql_dedup}\""
stdin, stdout, stderr = client.exec_command(cmd)
print("Stdout deduplication:")
print(stdout.read().decode('utf-8', errors='replace'))
print("Stderr deduplication:")
print(stderr.read().decode('utf-8', errors='replace'))

print("\nVerifying assignments count for KARINA MENDEZ...")
cmd_verify = "docker exec ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c \"SELECT u.name, upa.id, upa.printer_id, upa.entry_index, upa.is_active FROM user_printer_assignments upa JOIN users u ON u.id = upa.user_id WHERE u.name ILIKE '%KARINA MENDEZ%';\""
stdin, stdout, stderr = client.exec_command(cmd_verify)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
