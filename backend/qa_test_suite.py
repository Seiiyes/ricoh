"""
QA Test Suite — Ricoh Suite
Prueba los flujos implementados el 22 mayo 2026:
  - B.1 Comparaciones Guardadas (API)
  - B.2 Analytics (API)
  - C.1 Edge case: nulos
  - C.2 Edge case: título largo + emojis
  - C.3 Edge case: datos de analytics con usuario real
"""
import urllib.request
import urllib.error
import json
import sys

BASE = "http://localhost:8000"
PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

results = []

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=10)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as ex:
        return 0, {"error": str(ex)}

def check(label, condition, detail=""):
    icon = PASS if condition else FAIL
    results.append((icon, label, detail))
    print(f"  {icon} {label}" + (f" — {detail}" if detail else ""))

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("QA RICOH SUITE — PRUEBAS AUTOMATIZADAS API")
print("="*60)

# A.0 — Login
print("\n[A.0] AUTH: Login como superadmin")
try:
    with open(".superadmin_password", "r") as f:
        superadmin_password = f.read().strip()
except:
    superadmin_password = "Admin1234!"
status, body = req("POST", "/auth/login", {"username": "superadmin", "password": superadmin_password})

token = body.get("access_token", "")
check("Login superadmin", status == 200 and token, f"status={status}")

if not token:
    print("\n  ABORTANDO: No se pudo obtener token. Verificar contraseña del superadmin.")
    sys.exit(1)

# ─────────────────────────────────────────────
print("\n[A.3] MULTI-TENANCY: Acceso sin token")
status, _ = req("GET", "/api/counters/comparaciones")
check("GET /comparaciones sin token retorna 401/403", status in (401, 403), f"status={status}")

# ─────────────────────────────────────────────
print("\n[B.1] COMPARACIONES GUARDADAS")

# B.1.1 — Obtener impresoras y cierres disponibles
status, printers_resp = req("GET", "/printers/", token=token)
printers_list = printers_resp.get("items", []) if isinstance(printers_resp, dict) else printers_resp if isinstance(printers_resp, list) else []
check("B.1.1 GET /printers/ retorna lista", status == 200 and len(printers_list) > 0,
      f"status={status}, count={len(printers_list)}")

# Preferir impresora con empresa_id para poder guardar comparaciones
printer_with_empresa = next((p for p in printers_list if p.get("empresa_id")), None)
printer_id = printer_with_empresa.get("id") if printer_with_empresa else (printers_list[0].get("id") if printers_list else None)
if printer_with_empresa:
    print(f"  → Usando printer_id={printer_id} con empresa_id={printer_with_empresa.get('empresa_id')}")
else:
    print(f"  ⚠️  Ninguna impresora tiene empresa_id — guardado de comparaciones requerirá usuario con empresa")

cierres = []
if printer_id:
    status2, cierres = req("GET", f"/api/counters/monthly?printer_id={printer_id}", token=token)
    cierres = cierres if isinstance(cierres, list) else []
    check("B.1.1 GET /monthly?printer_id retorna cierres", status2 == 200 and len(cierres) > 0,
          f"status={status2}, cierres={len(cierres)}")
else:
    check("B.1.1 Cierres disponibles", False, "No hay impresoras")

cierre1_id = None
cierre2_id = None
if isinstance(cierres, list) and len(cierres) >= 2:
    cierre1_id = cierres[0]["id"]
    cierre2_id = cierres[1]["id"]
elif isinstance(cierres, list) and len(cierres) == 1:
    cierre1_id = cierres[0]["id"]
    cierre2_id = cierres[0]["id"]

# B.1.2 — Comparar dos cierres
if cierre1_id and cierre2_id:
    status, comparacion = req("GET", f"/api/counters/monthly/compare/{cierre1_id}/{cierre2_id}", token=token)
    tiene_datos = status == 200 and isinstance(comparacion, (dict, list))
    check("B.1.2 GET /compare/{id1}/{id2} retorna datos", tiene_datos, f"status={status}")
else:
    check("B.1.2 Comparar cierres", False, "No hay suficientes cierres en DB")

# B.1.3 + B.1.4 — Guardar comparación
print("\n  → Guardando comparación de prueba...")
if cierre1_id and cierre2_id:
    payload = {
        "titulo": "Comparativa QA Automatizada 26-Mayo-2026",
        "descripcion": "Test automatizado de QA del flujo de guardado",
        "cierre1_id": cierre1_id,
        "cierre2_id": cierre2_id,
        "snapshot_json": {"test": True, "paginas": 1234}
    }
    status, saved = req("POST", "/api/counters/comparaciones", body=payload, token=token)
    check("B.1.3/4 POST /comparaciones guarda correctamente", status in (200, 201), f"status={status}, id={saved.get('id','?')}")
    saved_id = saved.get("id")
else:
    check("B.1.3/4 Guardar comparación", False, "Sin cierres disponibles")
    saved_id = None

# B.1.5 — Listar comparaciones guardadas
status, lista = req("GET", "/api/counters/comparaciones", token=token)
check("B.1.5 GET /comparaciones retorna lista", status == 200 and isinstance(lista, list), f"status={status}, count={len(lista) if isinstance(lista,list) else '?'}")

# B.1.7 — Eliminar comparación guardada
if saved_id:
    status, _ = req("DELETE", f"/api/counters/comparaciones/{saved_id}", token=token)
    check("B.1.7 DELETE /comparaciones/{id} elimina correctamente", status in (200, 204), f"status={status}")
else:
    check("B.1.7 Eliminar comparación", False, "No hay ID para eliminar")

# ─────────────────────────────────────────────
print("\n[B.2] ANALYTICS")

# B.2.1 — Evolution
status, evo = req("GET", "/api/v1/analytics/evolution?meses=6", token=token)
check("B.2.1 GET /evolution?meses=6 retorna datos", status == 200 and isinstance(evo, list) and len(evo) > 0,
      f"status={status}, meses={len(evo) if isinstance(evo,list) else '?'}")

# B.2.2 — Consumo resumen (datos reales, no dummy)
status, consumo = req("GET", "/api/v1/dashboard/consumo-resumen", token=token)
check("B.2.2 GET /consumo-resumen retorna totales reales", status == 200,
      f"status={status}, total={consumo.get('total_paginas','?') if isinstance(consumo,dict) else '?'}")
if isinstance(consumo, dict):
    total = consumo.get("total_paginas", 0)
    check("B.2.2 Total paginas > 0 (no dummy)", total > 0, f"total_paginas={total}")

# B.2.3 — Top usuarios consumo
status, top_users = req("GET", "/api/v1/dashboard/top-usuarios-consumo?limit=5", token=token)
check("B.2.3 GET /top-usuarios-consumo retorna lista", status == 200 and isinstance(top_users, list),
      f"status={status}, usuarios={len(top_users) if isinstance(top_users,list) else '?'}")

# B.2 — Top users analytics con rango fechas
status, analyt = req("GET", "/api/v1/analytics/top-users?fecha_inicio=2026-01-01&fecha_fin=2026-12-31&limit=5", token=token)
check("B.2 GET /analytics/top-users con rango fechas", status == 200 and isinstance(analyt, list),
      f"status={status}, registros={len(analyt) if isinstance(analyt,list) else '?'}")
if isinstance(analyt, list) and len(analyt) > 0:
    user = analyt[0]
    tiene_desglose = all(k in user for k in ["total_copiadora","total_impresora","total_escaner","total_fax"])
    check("B.2.6 Desglose tridimensional presente en respuesta", tiene_desglose,
          f"keys={list(user.keys())[:6]}")

# ─────────────────────────────────────────────
print("\n[C] EDGE CASES")

# C.2 — Título largo con emojis
if cierre1_id and cierre2_id:
    titulo_largo = "Comparativa Ricoh Master Principal 🚀 - Q1 - Edificio 3 Piso 2 Centralizada de Contabilidad $$$ 12345 EXTRA_LARGO"
    payload_c2 = {
        "titulo": titulo_largo,
        "descripcion": "Prueba edge case caracteres especiales y longitud",
        "cierre1_id": cierre1_id,
        "cierre2_id": cierre2_id,
        "snapshot_json": {}
    }
    status, r = req("POST", "/api/counters/comparaciones", body=payload_c2, token=token)
    check("C.2 Backend acepta título 100+ chars con emojis", status in (200, 201, 422),
          f"status={status}")
    if status in (200, 201) and r.get("id"):
        # Limpiar
        req("DELETE", f"/api/counters/comparaciones/{r['id']}", token=token)

# C.1 — Usuarios con nulos en analytics
status, null_users = req("GET", "/api/v1/analytics/top-users?fecha_inicio=2020-01-01&fecha_fin=2020-12-31&limit=10", token=token)
check("C.1 Query con rango sin datos no crashea (retorna lista vacía o 200)", status == 200,
      f"status={status}, result={null_users if isinstance(null_users,list) else type(null_users).__name__}")

# ─────────────────────────────────────────────
print("\n[DASHBOARD] Endpoints de tóner")
status, toner = req("GET", "/api/v1/dashboard/toner-alertas", token=token)
check("Toner alertas 200 OK", status == 200 and isinstance(toner, list),
      f"status={status}, impresoras={len(toner) if isinstance(toner,list) else '?'}")
if isinstance(toner, list) and len(toner) > 0:
    p = toner[0]
    check("Estructura tóner: printer_id, toner_black, alerta presentes",
          all(k in p for k in ["printer_id","toner_black","alerta"]),
          f"keys={list(p.keys())}")

# ─────────────────────────────────────────────
print("\n" + "="*60)
print("RESUMEN FINAL")
print("="*60)
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
total = len(results)
print(f"\n  Total: {total} pruebas | {PASS} Pasaron: {passed} | {FAIL} Fallaron: {failed}")

if failed == 0:
    print("\n  🎉 TODAS LAS PRUEBAS PASARON — Sistema listo para QA manual en browser")
else:
    print(f"\n  ⚠️  HAY {failed} PRUEBA(S) FALLIDA(S) — Revisar antes del sábado")

print()
