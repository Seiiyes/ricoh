import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST, USER, PASS = "192.168.91.131", "odootic", "Zuly152325*"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    
    # Ping all printers
    for ip in ["192.168.91.250", "192.168.91.251", "192.168.91.252", "192.168.91.253"]:
        cmd = f"ping -c 1 -W 2 {ip}"
        _, stdout, _ = client.exec_command(cmd)
        print(f"=== PING {ip} ===")
        print(stdout.read().decode('utf-8', errors='replace').strip())

    # Copy file from container to host VM temp directory, then download it via SFTP
    client.exec_command("docker cp ricoh-backend:/app/debug_step2_fail.html /home/odootic/debug_step2_fail.html")
        
    sftp = client.open_sftp()
    local_path = r"c:\Users\juan.lizarazo\Desktop\ricoh\debug_step2_fail.html"
    try:
        sftp.get("/home/odootic/debug_step2_fail.html", local_path)
        print(f"Downloaded debug_step2_fail.html to {local_path}")
        client.exec_command("rm /home/odootic/debug_step2_fail.html")
    except Exception as e_get:
        print(f"Could not download: {e_get}")
            
    sftp.close()
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
