import paramiko
import hashlib
import os

HOST, USER, PASS = "192.168.91.131", "odootic", "Zuly152325*"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

files = [
    "backend/services/ricoh_web_client.py",
    "backend/api/discovery.py",
    "backend/api/counters.py"
]

def get_md5(path):
    if not os.path.exists(path):
        return "LOCAL_MISSING"
    h = hashlib.md5()
    with open(path, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

try:
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    sftp = client.open_sftp()
    
    print(f"{'Archivo':<40} | {'MD5 Local':<32} | {'MD5 Remoto':<32} | {'Estado':<10}")
    print("-" * 125)
    
    for rel_path in files:
        local_path = os.path.join(r"c:\Users\juan.lizarazo\Desktop\ricoh", rel_path.replace('/', '\\'))
        remote_path = f"/home/odootic/ricoh-app/{rel_path}"
        
        local_md5 = get_md5(local_path)
        
        try:
            # Get remote content hash
            with sftp.open(remote_path, 'rb') as f:
                remote_data = f.read()
                remote_md5 = hashlib.md5(remote_data).hexdigest()
        except FileNotFoundError:
            remote_md5 = "REMOTE_MISSING"
            
        status = "IDÉNTICO" if local_md5 == remote_md5 else "DIFERENTE"
        print(f"{rel_path:<40} | {local_md5:<32} | {remote_md5:<32} | {status:<10}")
        
    sftp.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
