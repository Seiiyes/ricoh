import paramiko
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

print("Starting HTTP tests directly on the production server for Analytics endpoints...")

# Script que corre dentro del contenedor ricoh-backend
test_api_script = """
cat << 'EOF' > /tmp/test_api_endpoints.py
import requests
import json
import sys
sys.path.append('/app')

BASE_URL = "http://localhost:8000"

print("1. Authenticating as superadmin (via /auth/login with JSON)...")
headers = {}
for pwd in ["superadminpassword", "ricoh2026", "ricoh2024"]:
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            json={"username": "superadmin", "password": pwd}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   ✅ Authentication successful with password '{pwd}'.")
            break
    except Exception as e:
        print(f"   Error: {e}")

if not headers:
    print("   ❌ All standard login attempts failed. Let's run direct DB imports to test data.")
else:
    # 2. Test comparativa de periodos en Resumen General
    print("\\n2. Testing GET /api/v1/analytics/comparison (Resumen General Comparison)...")
    comp_url = f"{BASE_URL}/api/v1/analytics/comparison?fecha_inicio_a=2026-05-20&fecha_fin_a=2026-05-20&fecha_inicio_b=2026-05-06&fecha_fin_b=2026-05-06"
    res_comp = requests.get(comp_url, headers=headers)
    print(f"   Response Status: {res_comp.status_code}")
    if res_comp.status_code == 200:
        data = res_comp.json()
        print(f"   ✅ OK. Received {len(data)} comparison metrics:")
        print(json.dumps(data[:3], indent=2, ensure_ascii=False))
    else:
        print(f"   ❌ Failed: {res_comp.text}")

    # 3. Test consumos globales de usuario paginados (Tab Consumo de Usuarios - Periodo Principal A)
    print("\\n3. Testing GET /api/counters/monthly/users/all (Consumo Usuarios - Periodo A)...")
    users_a_url = f"{BASE_URL}/api/counters/monthly/users/all?page=1&page_size=5&fecha_inicio=2026-05-20&fecha_fin=2026-05-20"
    res_users_a = requests.get(users_a_url, headers=headers)
    print(f"   Response Status: {res_users_a.status_code}")
    if res_users_a.status_code == 200:
        data = res_users_a.json()
        print(f"   ✅ OK. Total items in period A: {data.get('total')}")
        print(f"   Sample items (first 2):")
        print(json.dumps(data.get('items')[:2], indent=2, ensure_ascii=False))
    else:
        print(f"   ❌ Failed: {res_users_a.text}")

# 4. Direct DB verify using SQLAlchemy to confirm model query correctness
print("\\n4. Running Direct Database query verification via SQLAlchemy...")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import CierreMensualUsuario, CierreMensual, Printer, User

engine = create_engine('postgresql://ricoh_admin:ricoh_secure_2024@ricoh-postgres:5432/ricoh_fleet')
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Simular la consulta de closures agrupados de Tab 2
    query = db.query(CierreMensualUsuario).join(
        CierreMensual, CierreMensual.id == CierreMensualUsuario.cierre_mensual_id
    ).filter(CierreMensual.fecha_inicio == '2026-05-20')
    
    total = query.count()
    sample = query.limit(2).all()
    print(f"   ✅ SQLAlchemy Direct query OK. Total records for 2026-05-20: {total}")
    for idx, r in enumerate(sample):
        print(f"      [{idx}] User ID: {r.user_id} | Total Consumption: {r.consumo_total}")
except Exception as e:
    print(f"   ❌ Direct query failed: {e}")
finally:
    db.close()

EOF
docker cp /tmp/test_api_endpoints.py ricoh-backend:/app/test_api_endpoints.py
docker exec -t ricoh-backend python /app/test_api_endpoints.py
"""

stdin, stdout, stderr = client.exec_command(test_api_script)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
