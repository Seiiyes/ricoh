import paramiko
import sys

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

python_code = """
from db.database import SessionLocal
from db.models import User
db = SessionLocal()
try:
    user = db.query(User).filter(User.codigo_de_usuario == "7104").first()
    if user:
        print(f"Name: {user.name}")
        print(f"Codigo: {user.codigo_de_usuario}")
        print(f"Copiadora (func_copier): {user.func_copier}")
        print(f"Copiadora Color (func_copier_color): {user.func_copier_color}")
        print(f"Impresora (func_printer): {user.func_printer}")
        print(f"Impresora Color (func_printer_color): {user.func_printer_color}")
        print(f"Scanner (func_scanner): {user.func_scanner}")
        print(f"Document Server (func_document_server): {user.func_document_server}")
        print(f"Fax (func_fax): {user.func_fax}")
        print(f"Browser (func_browser): {user.func_browser}")
    else:
        print("User 7104 not found")
finally:
    db.close()
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    with sftp.open('/home/odootic/ricoh-app/backend/test_inspect_user.py', 'w') as f:
        f.write(python_code)
    sftp.close()
    
    stdin, stdout, stderr = client.exec_command("echo 'Zuly152325*' | sudo -S docker exec ricoh-backend python test_inspect_user.py")
    print(stdout.read().decode('utf-8', errors='replace').strip())
    print(stderr.read().decode('utf-8', errors='replace').strip())
    
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_inspect_user.py")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
