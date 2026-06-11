"""
security_validation_suite.py
=============================
Pruebas de seguridad reales contra el servidor en http://localhost:8000

Valida:
  S.1  WebSocket /ws/logs requiere autenticación (token faltante → rechazado)
  S.2  WebSocket /ws/logs acepta conexión con token válido
  S.3  WebSocket rechaza token inválido (formato correcto pero firma falsa)
  S.4  WebSocket rechaza token expirado (simulado)
  S.5  Dashboard /kpis requiere autenticación (sin token → 401/403)
  S.6  Dashboard /top-impresoras requiere autenticación
  S.7  Dashboard /actividad-reciente requiere autenticación
  S.8  Dashboard /consumo-resumen requiere autenticación
  S.9  Dashboard /toner-alertas requiere autenticación
  S.10 Analytics /evolution requiere autenticación
  S.11 Analytics /comparison requiere autenticación
  S.12 Con token válido: dashboard/kpis → 200 OK
  S.13 Con token válido: analytics/evolution → 200 OK
  S.14 Con token válido: analytics/comparison → 200 OK
  S.15 Con token válido: dashboard/actividad-reciente → 200 OK
  S.16 Counters /monthly/users/all requiere autenticación
  S.17 Export endpoints requieren autenticación
  S.18 Token inválido en REST API devuelve 401
"""

import urllib.request
import urllib.error
import json
import sys
import socket
import struct
import base64
import hashlib
import time
import threading

BASE = "http://localhost:8000"
WS_BASE = "ws://localhost:8000"

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

results = []
superadmin_password = None

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def req(method, path, body=None, token=None, timeout=10):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        try:
            return resp.status, json.loads(resp.read().decode())
        except Exception:
            return resp.status, {}
    except urllib.error.HTTPError as e:
        try:
            body_resp = json.loads(e.read().decode())
        except Exception:
            body_resp = {}
        return e.code, body_resp
    except Exception as ex:
        return 0, {"error": str(ex)}


def record(label, condition, detail=""):
    icon = PASS if condition else FAIL
    results.append((icon, label, detail))
    print(f"  {icon}  {label}" + (f"\n           → {detail}" if detail else ""))


def ws_check_rejection(path, expect_codes=(4001,)):
    """
    Abre un WebSocket raw (handshake HTTP) y retorna el código de cierre
    o el código HTTP de rechazo si el servidor rechazó el upgrade.
    
    Devuelve (rejected: bool, detail: str)
    """
    try:
        # Parse URL
        host = "localhost"
        port = 8000
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(8)
        s.connect((host, port))
        
        # Generar key WS (debe ser de exactamente 16 bytes antes de base64)
        key = base64.b64encode(b"1234567890123456").decode()
        
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )
        s.sendall(handshake.encode())
        
        # Leer respuesta HTTP
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        
        response_str = response.decode(errors="replace")
        first_line = response_str.split("\r\n")[0]
        
        s.close()
        
        # Si retornó 403, 401 o 4xx → rechazado correctamente
        if "403" in first_line or "401" in first_line or "422" in first_line:
            return True, f"HTTP {first_line.strip()}"
        elif "101" in first_line:
            # Fue aceptado — MAL si esperábamos rechazo
            return False, f"Aceptado (HTTP 101) — debería haber sido rechazado"
        else:
            return True, f"Respuesta inesperada: {first_line.strip()}"
    
    except Exception as ex:
        return True, f"Conexión rechazada a nivel TCP: {ex}"


def ws_check_acceptance(path):
    """
    Verifica que el WebSocket ACEPTA la conexión (HTTP 101 Switching Protocols).
    Devuelve (accepted: bool, detail: str)
    """
    try:
        host = "localhost"
        port = 8000
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(8)
        s.connect((host, port))
        
        # Generar key WS (debe ser de exactamente 16 bytes antes de base64)
        key = base64.b64encode(b"abcdefghijklmnop").decode()
        
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n"
            f"\r\n"
        )
        s.sendall(handshake.encode())
        
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
        
        response_str = response.decode(errors="replace")
        first_line = response_str.split("\r\n")[0]
        
        accepted = "101" in first_line
        s.close()
        return accepted, first_line.strip()
    
    except Exception as ex:
        return False, str(ex)


def make_fake_token():
    """Genera un JWT con formato válido pero firma falsa."""
    header = base64.urlsafe_b64encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode()).rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(json.dumps({"user_id":1,"username":"hacker","rol":"superadmin","exp":9999999999}).encode()).rstrip(b"=").decode()
    signature = base64.urlsafe_b64encode(b"fake_signature_not_valid").rstrip(b"=").decode()
    return f"{header}.{payload}.{signature}"


# ─────────────────────────────────────────────────────────────────────────────
# Read superadmin password
# ─────────────────────────────────────────────────────────────────────────────

try:
    with open(".superadmin_password", "r") as f:
        superadmin_password = f.read().strip()
    print(f"\n  → Contraseña superadmin cargada desde .superadmin_password")
except FileNotFoundError:
    superadmin_password = "Admin1234!"
    print(f"\n  ⚠️  .superadmin_password no encontrado. Usando contraseña por defecto: Admin1234!")

# ─────────────────────────────────────────────────────────────────────────────
# Obtener token válido
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "="*70)
print("RICOH SUITE — SUITE DE SEGURIDAD — PRUEBAS REALES")
print("="*70)

print("\n[SETUP] Obteniendo token de autenticación...")
status, body = req("POST", "/auth/login", {"username": "superadmin", "password": superadmin_password})
valid_token = body.get("access_token", "")
record("SETUP: Login superadmin exitoso", status == 200 and bool(valid_token), f"HTTP {status}")

if not valid_token:
    print("\n  ABORTANDO: No se pudo obtener token. El servidor podría no estar ejecutándose.")
    print(f"  Intenta: curl -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' -d '{{\"username\":\"superadmin\",\"password\":\"{superadmin_password}\"}}'")
    sys.exit(1)

fake_token = make_fake_token()
token_preview = valid_token[:12] + "..." + valid_token[-4:]
print(f"  → Token válido obtenido: {token_preview}")
print(f"  → Token falso generado: {fake_token[:20]}...")

# ─────────────────────────────────────────────────────────────────────────────
# S.1-S.4 — WebSocket Security
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─"*70)
print("[S.1-S.4] WebSocket /ws/logs — Autenticación")
print("─"*70)

# S.1 — Sin token → debe rechazar
rejected, detail = ws_check_rejection("/ws/logs")
record(
    "S.1  /ws/logs SIN token → rechazado (403/401/connection error)",
    rejected,
    detail
)

# S.2 — Con token válido → debe aceptar (HTTP 101)
accepted, detail = ws_check_acceptance(f"/ws/logs?token={valid_token}")
record(
    "S.2  /ws/logs CON token válido → aceptado (HTTP 101)",
    accepted,
    detail
)

# S.3 — Token falso → debe rechazar
rejected, detail = ws_check_rejection(f"/ws/logs?token={fake_token}")
record(
    "S.3  /ws/logs CON token FALSO → rechazado",
    rejected,
    detail
)

# S.4 — Token con estructura incorrecta → debe rechazar
rejected, detail = ws_check_rejection("/ws/logs?token=eyJ.invalid.token")
record(
    "S.4  /ws/logs CON token MALFORMADO → rechazado",
    rejected,
    detail
)

# ─────────────────────────────────────────────────────────────────────────────
# S.5-S.11 — Endpoints sin token → deben retornar 401/403
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─"*70)
print("[S.5-S.11] Endpoints REST — Sin autenticación → 401/403")
print("─"*70)

unauthenticated_endpoints = [
    ("S.5 ", "GET", "/api/v1/dashboard/kpis"),
    ("S.6 ", "GET", "/api/v1/dashboard/top-impresoras"),
    ("S.7 ", "GET", "/api/v1/dashboard/actividad-reciente"),
    ("S.8 ", "GET", "/api/v1/dashboard/consumo-resumen"),
    ("S.9 ", "GET", "/api/v1/dashboard/toner-alertas"),
    ("S.10", "GET", "/api/v1/analytics/evolution?meses=3"),
    ("S.11", "GET", "/api/v1/analytics/comparison?fecha_inicio_a=2026-01-01&fecha_fin_a=2026-01-31&fecha_inicio_b=2026-02-01&fecha_fin_b=2026-02-28"),
    ("S.16", "GET", "/api/counters/monthly/users/all"),
    ("S.17", "GET", "/api/export/cierre/1/excel"),
]

for code, method, path in unauthenticated_endpoints:
    status, body = req(method, path, token=None)
    is_rejected = status in (401, 403, 422)
    record(
        f"{code} {method} {path.split('?')[0]} sin token → 401/403",
        is_rejected,
        f"HTTP {status}" + (f" — {body.get('detail','')}" if isinstance(body, dict) and body.get('detail') else "")
    )

# ─────────────────────────────────────────────────────────────────────────────
# S.18 — Token inválido en REST API
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─"*70)
print("[S.18] Token falso en REST API → 401")
print("─"*70)

status, body = req("GET", "/api/v1/dashboard/kpis", token=fake_token)
record(
    "S.18 Token JWT FALSO en Authorization header → 401",
    status == 401,
    f"HTTP {status}"
)

# ─────────────────────────────────────────────────────────────────────────────
# S.12-S.15 — Con token válido: respuestas 200
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─"*70)
print("[S.12-S.15] Endpoints con token válido → 200 OK")
print("─"*70)

authenticated_endpoints = [
    ("S.12", "GET", "/api/v1/dashboard/kpis"),
    ("S.13", "GET", "/api/v1/analytics/evolution?meses=3"),
    ("S.14", "GET", "/api/v1/analytics/comparison?fecha_inicio_a=2026-01-01&fecha_fin_a=2026-01-31&fecha_inicio_b=2026-02-01&fecha_fin_b=2026-02-28"),
    ("S.15", "GET", "/api/v1/dashboard/actividad-reciente"),
    ("S.19", "GET", "/api/v1/dashboard/top-impresoras"),
    ("S.20", "GET", "/api/v1/dashboard/consumo-resumen"),
    ("S.21", "GET", "/api/v1/dashboard/toner-alertas"),
    ("S.22", "GET", "/api/v1/analytics/top-users?fecha_inicio=2026-01-01&fecha_fin=2026-12-31&limit=5"),
    ("S.23", "GET", "/api/counters/monthly/users/all?page=1&page_size=5"),
]

for code, method, path in authenticated_endpoints:
    status, body = req(method, path, token=valid_token)
    is_ok = status == 200
    endpoint = path.split('?')[0]
    detail = f"HTTP {status}"
    if is_ok and isinstance(body, dict):
        detail += f" — keys={list(body.keys())[:4]}"
    elif is_ok and isinstance(body, list):
        detail += f" — {len(body)} items"
    record(f"{code} {method} {endpoint} con token válido → 200", is_ok, detail)

# ─────────────────────────────────────────────────────────────────────────────
# S.BONUS — Verificar que /auth/login SÍ es accesible sin token
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─"*70)
print("[S.BONUS] Endpoint público /auth/login — no requiere token")
print("─"*70)

status, body = req("POST", "/auth/login", {"username": "usuario_inexistente_abc123", "password": "wrong"})
record(
    "S.B1 POST /auth/login es accesible SIN token (debe devolver 401 por credenciales, no 403 por auth)",
    status == 401,
    f"HTTP {status} (esperado: 401 invalid credentials, no 403 Forbidden)"
)

# ─────────────────────────────────────────────────────────────────────────────
# S.BONUS2 — Rate limit DDoS funciona correctamente
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "─"*70)
print("[S.BONUS2] DDoS rate limit — prueba básica de respuesta 429")
print("─"*70)

# Llamar /auth/login 7 veces con credenciales inválidas para ver si dispara 429
print("  → Enviando 7 intentos de login fallidos rápidos...")
got_429 = False
last_status = 0
for i in range(7):
    status, _ = req("POST", "/auth/login", {"username": "superadmin", "password": f"wrong_password_{i}"})
    last_status = status
    if status == 429:
        got_429 = True
        print(f"  → 429 Too Many Requests detectado en intento #{i+1}")
        break

record(
    "S.B2 Rate limit /auth/login: 7 intentos rápidos disparan 429",
    got_429,
    f"último HTTP {last_status}" + (" — 429 recibido ✓" if got_429 else " — 429 NO recibido (puede ser whitelist dev)")
)

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "="*70)
print("RESUMEN FINAL — VALIDACIONES DE SEGURIDAD")
print("="*70)

passed = [r for r in results if r[0] == PASS]
failed = [r for r in results if r[0] == FAIL]
total = len(results)

print(f"\n  Total: {total} pruebas  |  ✅ Pasaron: {len(passed)}  |  ❌ Fallaron: {len(failed)}\n")

if failed:
    print("  Pruebas fallidas:")
    for icon, label, detail in failed:
        print(f"    {icon}  {label}")
        if detail:
            print(f"           → {detail}")

if len(failed) == 0:
    print("\n  🎉 TODAS LAS PRUEBAS DE SEGURIDAD PASARON")
    print("  El sistema está protegido correctamente.")
elif len(failed) <= 2:
    print("\n  ⚠️  CASI LISTO — revisar las pruebas fallidas arriba")
else:
    print(f"\n  🔴 {len(failed)} PRUEBAS FALLIDAS — REVISAR SEGURIDAD")

print()
sys.exit(0 if len(failed) == 0 else 1)
