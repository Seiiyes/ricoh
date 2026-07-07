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

print("Auditing assignments of inactive users in the database...")
# Consulta SQL para buscar todas las asignaciones de impresoras para usuarios que tienen is_active = False,
# y verificar si hay alguna asignación con permisos en True.
sql_query = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
SELECT u.id as user_id, u.name, u.codigo_de_usuario, u.is_active as user_active,
       a.printer_id, a.is_active as assignment_active,
       a.func_copier, a.func_copier_color, a.func_printer, a.func_printer_color, 
       a.func_document_server, a.func_fax, a.func_scanner, a.func_browser
FROM users u
INNER JOIN user_printer_assignments a ON u.id = a.user_id
WHERE u.is_active = false AND (
    a.func_copier = true OR a.func_copier_color = true OR 
    a.func_printer = true OR a.func_printer_color = true OR 
    a.func_document_server = true OR a.func_fax = true OR 
    a.func_scanner = true OR a.func_browser = true
);
"
"""
stdin, stdout, stderr = client.exec_command(sql_query)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
