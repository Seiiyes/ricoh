import paramiko
import sys
import io
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("Checking `/users/` response body using python script in backend container...")

python_call = """
docker exec -t ricoh-backend python -c "
import urllib.request
import json
try:
    req = urllib.request.Request('http://localhost:8000/users/?page=1&page_size=5&active_only=false')
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        data = json.loads(html)
        print('SUCCESS')
        print(json.dumps(data))
except Exception as e:
    print('ERROR:', e)
"
"""

stdin, stdout, stderr = client.exec_command(python_call)
response_text = stdout.read().decode('utf-8', errors='replace')

if "SUCCESS" in response_text:
    json_part = response_text.replace("SUCCESS", "").strip()
    try:
        data = json.loads(json_part)
        items = data.get('items', [])
        print(f"Total Users: {data.get('total')}")
        print(f"Items Count: {len(items)}")
        if items:
            for item in items[:3]:
                print(f"\\nUser ID: {item.get('id')} | Name: {item.get('name')} | Is Active: {item.get('is_active')}")
                print(f"  Impresoras count: {len(item.get('impresoras', []))}")
                print(f"  Impresoras: {item.get('impresoras')}")
    except Exception as e:
        print("Error parsing json:", e)
        print("Raw text:", response_text[:1000])
else:
    print("Execution failed:")
    print(response_text)

client.close()
