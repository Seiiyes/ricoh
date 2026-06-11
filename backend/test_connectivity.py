"""Test de conectividad al backend."""
import urllib.request
import urllib.error
import json
import sys

# Intentar con diferentes hosts
HOSTS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://[::1]:8000",
    "http://192.168.91.34:8000",
]

print("=== TEST DE CONECTIVIDAD BACKEND ===\n")

working_base = None
for base in HOSTS:
    url = base + "/docs"
    try:
        r = urllib.request.urlopen(url, timeout=5)
        print(f"  CONECTADO: {base} -> HTTP {r.status}")
        working_base = base
        break
    except urllib.error.HTTPError as e:
        print(f"  HTTP ERROR: {base} -> {e.code}")
        working_base = base
        break
    except Exception as ex:
        print(f"  FALLO: {base} -> {ex}")

if not working_base:
    print("\n  ERROR: No se pudo conectar al backend en ningun host.")
    sys.exit(1)

print(f"\n  Usando: {working_base}")

# Intentar login
print("\n=== TEST LOGIN ===\n")
try:
    with open(".superadmin_password", "r") as f:
        pwd = f.read().strip()
    print(f"  Password leido: {pwd[:4]}****")
except:
    pwd = "Admin1234!"
    print(f"  Usando password por defecto")

body = json.dumps({"username": "superadmin", "password": pwd}).encode()
req = urllib.request.Request(
    working_base + "/auth/login",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST"
)
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode())
    token = data.get("access_token", "")
    print(f"  LOGIN OK - HTTP {resp.status}")
    print(f"  Token: {token[:15]}...")
except urllib.error.HTTPError as e:
    body_resp = e.read().decode()
    print(f"  LOGIN FALLO - HTTP {e.code}: {body_resp[:200]}")
    sys.exit(1)
except Exception as ex:
    print(f"  ERROR: {ex}")
    sys.exit(1)

# Test endpoint sin auth
print("\n=== TEST SIN AUTH ===\n")
req2 = urllib.request.Request(working_base + "/api/v1/dashboard/kpis", method="GET")
try:
    resp2 = urllib.request.urlopen(req2, timeout=10)
    print(f"  PROBLEMA: /dashboard/kpis sin auth retorno HTTP {resp2.status} (deberia ser 401)")
except urllib.error.HTTPError as e:
    print(f"  CORRECTO: /dashboard/kpis sin auth retorno HTTP {e.code}")
except Exception as ex:
    print(f"  ERROR: {ex}")

print("\n=== CONNECTIVITY OK ===")
print(f"Base URL funcional: {working_base}")
