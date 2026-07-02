import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST, USER, PASS = "192.168.91.131", "odootic", "Zuly152325*"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    print(f"[OK] Conectado a {HOST}")
    
    # 1. Obtener estado de docker compose ps
    cmd = f"echo '{PASS}' | sudo -S docker compose -f /home/odootic/ricoh-app/docker-compose.yml ps"
    _, stdout, stderr = client.exec_command(cmd)
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    print("\n=== DOCKER COMPOSE PS ===")
    print(out)
    if err and "password" not in err.lower(): # Omitir sudo password warning
        print("\n=== ERRORS/WARNINGS ===")
        print(err)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
