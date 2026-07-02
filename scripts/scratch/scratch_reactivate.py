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
from db.models import User, UserPrinterAssignment

db = SessionLocal()
u = db.query(User).filter(User.codigo_de_usuario == '7104').first()
if not u:
    print('User 7104 not found')
else:
    u.is_active = True
    print(f'Reactivated user: ID={u.id}, name={u.name}')
    
    assignments = db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == u.id).all()
    reactivated_count = 0
    for a in assignments:
        a.is_active = True
        reactivated_count += 1
    
    db.commit()
    print(f'Reactivated {reactivated_count} assignments for user {u.name}')
"""
    
    # Write the script on the server
    sftp = client.open_sftp()
    with sftp.open('/home/odootic/ricoh-app/backend/test_reactivate.py', 'w') as f:
        f.write(script_content)
    sftp.close()
    
    # Run the script inside the docker container
    cmd = f"echo '{PASS}' | sudo -S docker exec ricoh-backend python test_reactivate.py"
    stdin, stdout, stderr = client.exec_command(cmd)
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    print("\nOUTPUT:")
    print(out)
    if err:
        print("\nERROR:")
        print(err)
        
    # Clean up the script
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_reactivate.py")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
