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

print("Cleaning up inconsistent printer assignments for inactive users...")
# Sentencia SQL para desactivar (poner is_active = false y todos los permisos en false) 
# en user_printer_assignments para cualquier usuario que esté desactivado (is_active = false) en users.
sql_clean = """
docker exec -t ricoh-postgres psql -U ricoh_admin -d ricoh_fleet -c "
UPDATE user_printer_assignments 
SET is_active = false,
    func_copier = false,
    func_copier_color = false,
    func_printer = false,
    func_printer_color = false,
    func_document_server = false,
    func_fax = false,
    func_scanner = false,
    func_browser = false
WHERE user_id IN (SELECT id FROM users WHERE is_active = false);
"
"""
stdin, stdout, stderr = client.exec_command(sql_clean)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
