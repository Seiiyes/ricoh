import paramiko
import sys

# Configure stdout to use utf-8 to avoid charmap issues on Windows
sys.stdout.reconfigure(encoding='utf-8')

HOST = "192.168.91.131"
USER = "odootic"
PASS = "Zuly152325*"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    print(f"Connected to {HOST}")
    
    script_content = """
from db.database import SessionLocal
from db.models_auth import AdminAuditLog
from db.models import User
import json

db = SessionLocal()

# Find the user record
u = db.query(User).filter(User.codigo_de_usuario == '7104').first()
if not u:
    print('User 7104 not found')
else:
    print(f'User 7104: ID={u.id}, name={u.name}, is_active={u.is_active}')
    
    # Query audit logs relating to this user
    logs = db.query(AdminAuditLog).filter(
        (AdminAuditLog.entidad_id == u.id) | 
        (AdminAuditLog.entidad_tipo == 'User') | 
        (AdminAuditLog.entidad_tipo == 'users')
    ).order_by(AdminAuditLog.created_at.desc()).all()
    
    print(f'Total matched logs: {len(logs)}')
    for log in logs[:15]:
        print(f'  Log ID: {log.id}, Time: {log.created_at}, Action: {log.accion}, Module: {log.modulo}, Result: {log.resultado}')
        print(f'    Entity: {log.entidad_tipo} (ID: {log.entidad_id})')
        if log.detalles:
            print(f'    Detalles: {log.detalles}')
"""
    
    # Write the script on the server
    sftp = client.open_sftp()
    with sftp.open('/home/odootic/ricoh-app/backend/test_check_audit.py', 'w') as f:
        f.write(script_content)
    sftp.close()
    
    # Run the script inside the docker container
    cmd = f"echo '{PASS}' | sudo -S docker exec ricoh-backend python test_check_audit.py"
    stdin, stdout, stderr = client.exec_command(cmd)
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    print("\nOUTPUT:")
    print(out)
    if err:
        print("\nERROR:")
        print(err)
        
    # Clean up the script
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_check_audit.py")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
