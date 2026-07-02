import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST, USER, PASS = "192.168.91.131", "odootic", "Zuly152325*"
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

for fname in ['password_step2_error.html', 'password_step3_error.html', 'password_error_response.html']:
    try:
        remote = f"/home/odootic/ricoh-app/{fname}"
        local = rf"C:\Users\juan.lizarazo\.gemini\antigravity-ide\brain\b7dd34cc-fe75-4a2b-94b2-869a2b2154f7\{fname}"
        sftp.get(remote, local)
        print(f"[OK] Descargado: {fname}")
    except Exception as e:
        print(f"[--] {fname}: {e}")

sftp.close()
client.close()
