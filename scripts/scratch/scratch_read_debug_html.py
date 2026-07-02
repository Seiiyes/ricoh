import paramiko

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    sftp = client.open_sftp()
    
    # Intentar leer el archivo guardado en el backend
    # Nota: El contenedor tiene montado /tmp? O el script guardó a /tmp del contenedor.
    # Si fue dentro del contenedor, tenemos que copiarlo o leerlo vía docker exec.
    stdin, stdout, stderr = client.exec_command("docker exec ricoh-backend head -n 100 /tmp/debug_no_checkboxes_00257.html")
    content = stdout.read().decode('utf-8', errors='replace')
    print("--- HTML CONTENT (First 100 lines) ---")
    print(content)
    
except Exception as e:
    print(f"Error: {e}")
finally:
    client.close()
