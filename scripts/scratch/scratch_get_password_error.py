import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    print("Connected to SSH")
    
    # Download file via SFTP
    sftp = client.open_sftp()
    remote_path = "/home/odootic/ricoh-app/backend/password_error_response.html"
    local_path = r"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain\b7dd34cc-fe75-4a2b-94b2-869a2b2154f7\password_error_response.html"
    
    try:
        sftp.get(remote_path, local_path)
        print(f"Downloaded to {local_path}")
    except FileNotFoundError:
        print("Remote file not found on host directory, checking docker...")
        # Check inside docker container by copying it out to host first
        client.exec_command("docker cp ricoh-backend:/app/password_error_response.html /home/odootic/ricoh-app/backend/password_error_response.html")
        sftp.get(remote_path, local_path)
        print(f"Downloaded from docker to {local_path}")
        
    sftp.close()
            
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
