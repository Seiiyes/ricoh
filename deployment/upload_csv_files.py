import paramiko
import sys
import io
import os
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

local_docs_dir = Path("c:/Users/juan.lizarazo/Desktop/ricoh/docs")
remote_docs_dir = "/home/odootic/ricoh-app/docs"

files_to_upload = [
    "E174M210096 19.06.2026.csv",
    "E174MA11130 19.06.2026.csv",
    "E176M460020 19.06.2026.csv",
    "G986XA16285 19.06.2026.csv",
    "W533L900719 19.06.2026.csv",
    "WhatsApp Image 2026-07-06 at 7.51.12 AM.jpeg",
    "WhatsApp Image 2026-07-06 at 7.51.18 AM.jpeg",
    "WhatsApp Image 2026-07-06 at 7.51.23 AM.jpeg",
    "WhatsApp Image 2026-07-06 at 7.51.30 AM.jpeg",
    "WhatsApp Image 2026-07-06 at 7.51.37 AM.jpeg"
]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

sftp = client.open_sftp()

print("Uploading CSV and Image files to production server via SFTP...")
for filename in files_to_upload:
    local_path = local_docs_dir / filename
    remote_path = f"{remote_docs_dir}/{filename}"
    
    if local_path.exists():
        print(f"Uploading {filename} -> {remote_path} ...")
        sftp.put(str(local_path), remote_path)
    else:
        print(f"⚠️ Local file not found: {local_path}")

sftp.close()
client.close()
print("Upload completed successfully!")
