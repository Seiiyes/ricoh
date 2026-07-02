import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST, USER, PASS = "192.168.91.131", "odootic", "Zuly152325*"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

# Find the HTML error files inside docker container
_, out, _ = client.exec_command('docker exec ricoh-backend find / -name "password_step2_error.html" 2>/dev/null')
found = out.read().decode('utf-8', errors='replace').strip()
print("Files found in docker:", found if found else "(none)")

if found:
    path = found.split('\n')[0]
    _, out2, _ = client.exec_command(f'docker exec ricoh-backend cat "{path}"')
    content = out2.read().decode('utf-8', errors='replace')
    print("=== CONTENT ===")
    print(content[:3000])
else:
    # Check container working dir
    _, out3, _ = client.exec_command('docker exec ricoh-backend pwd')
    print("Container workdir:", out3.read().decode().strip())
    _, out4, _ = client.exec_command('docker exec ricoh-backend ls -la')
    print("Container files:", out4.read().decode().strip())

# Also show last 60 lines of backend logs
_, out5, _ = client.exec_command('docker logs ricoh-backend --tail=60 2>&1')
print("\n=== BACKEND LOGS ===")
print(out5.read().decode('utf-8', errors='replace'))

client.close()
