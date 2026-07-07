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

print("Auditing user with code '8436' (ANGIE MUÑOZ) in production DB...")

# Script SQL para ver el usuario y sus asignaciones
db_query = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT id, name, codigo_de_usuario, is_active, func_copier, func_printer, func_scanner FROM users WHERE codigo_de_usuario = '8436';
SELECT 
    upa.id as assignment_id,
    upa.printer_id,
    p.hostname,
    upa.is_active,
    upa.func_copier,
    upa.func_printer,
    upa.func_scanner,
    upa.entry_index
FROM user_printer_assignments upa
INNER JOIN printers p ON p.id = upa.printer_id
WHERE upa.user_id = (SELECT id FROM users WHERE codigo_de_usuario = '8436');
"
"""

stdin, stdout, stderr = client.exec_command(db_query)
print(stdout.read().decode('utf-8', errors='replace'))
client.close()
