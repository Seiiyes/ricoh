import paramiko

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

python_code = """
from db.database import SessionLocal
from db.models import Printer
from services.ricoh_web_client import get_ricoh_web_client

db = SessionLocal()
try:
    printer = db.query(Printer).filter(Printer.ip_address == "192.168.91.250").first()
    if not printer:
        print("Printer 192.168.91.250 not found in DB")
        sys.exit(1)
        
    client = get_ricoh_web_client()
    client.reset_session()
    
    print("Reading users from 192.168.91.250 address book...")
    users = client.read_users_from_printer(printer.ip_address, fast_list=True, admin_password=printer.admin_password)
    
    print(f"Total users found: {len(users)}")
    print("Listing first 10 users:")
    for idx, u in enumerate(users[:10]):
        print(f"  {idx+1}: index={u.get('entry_index')}, name={u.get('nombre')}, code={u.get('codigo')}")
        
    # Search specifically for code 7104 or index 00257
    print("\\nSearching for code 7104 or index 00257:")
    for u in users:
        if u.get('codigo') == '7104' or u.get('entry_index') == '00257':
            print(f"  FOUND: index={u.get('entry_index')}, name={u.get('nombre')}, code={u.get('codigo')}")
            
except Exception as e:
    import traceback
    print("Error:", e)
    print(traceback.format_exc())
finally:
    db.close()
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    with sftp.open('/home/odootic/ricoh-app/backend/test_check_book.py', 'w') as f:
        f.write(python_code)
    sftp.close()
    
    stdin, stdout, stderr = client.exec_command("echo 'Zuly152325*' | sudo -S docker exec ricoh-backend python test_check_book.py")
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_check_book.py")
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
