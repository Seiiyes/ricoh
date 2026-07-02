import paramiko
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

local_base = r"c:\Users\juan.lizarazo\Desktop\ricoh"
remote_base = "/home/odootic/ricoh-app"

files_to_deploy = [
    "backend/services/ricoh_web_client.py",
    "backend/services/ricoh_password_flow.py",
    "backend/services/retry_strategy.py",
    "backend/api/discovery.py",
    "backend/api/counters.py",
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    print(f"[OK] CONECTADO a {HOST}")
    
    sftp = client.open_sftp()
    for rel_path in files_to_deploy:
        import os
        local_path = os.path.join(local_base, rel_path.replace('/', '\\'))
        remote_path = f"{remote_base}/{rel_path}"
        backup_path = f"{remote_path}.bak"
        
        print(f"\n📁 {rel_path}")
        try:
            sftp.stat(remote_path)
            client.exec_command(f"cp {remote_path} {backup_path}")
            print(f"   💾 Backup: {backup_path}")
        except FileNotFoundError:
            pass
        sftp.put(local_path, remote_path)
        print(f"   ✅ Subido.")
    sftp.close()

    print("\nEsperando 3s a que uvicorn recargue...")
    time.sleep(3)
    
    _, stdout, _ = client.exec_command("docker logs ricoh-backend --tail=5")
    print("\nLogs del backend:")
    print(stdout.read().decode('utf-8', errors='replace').strip())
    print("\n🎉 Despliegue completo.")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
finally:
    client.close()
