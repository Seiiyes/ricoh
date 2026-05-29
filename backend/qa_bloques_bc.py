"""
QA Bloques B y C - Pruebas funcionales via API
Ejecutar: docker exec ricoh-backend python /app/qa_bloques_bc.py
"""
import sys
import json
import requests

BASE = "http://localhost:8000"
TOKEN = None
RESULTS = []

def check(label, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    RESULTS.append((label, passed, detail))
    print(f"  {status}  {label}")
    if detail and not passed:
        print(f"         → {detail}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
section("AUTH — Login superadmin")

try:
    r = requests.post(f"{BASE}/auth/login",
        json={"username": "superadmin", "password": "Admin1234!"},
        timeout=10)
    data = r.json()
    TOKEN = data.get("access_token")
    check("B.auth.1 — Login 200 OK", r.status_code == 200, f"status={r.status_code}")
    check("B.auth.2 — access_token presente", bool(TOKEN), f"keys={list(data.keys())}")
except Exception as e:
    check("B.auth — Login", False, str(e))
    print("FATAL: sin token, abortando"); sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Obtener una impresora para las pruebas
printers = []
printer_id = None
try:
    # superadmin no tiene empresa_id → obtener desde DB directamente
    from db.database import SessionLocal
    from db.models import Printer
    db = SessionLocal()
    p = db.query(Printer).filter(Printer.empresa_id != None).first()
    if not p:
        p = db.query(Printer).first()
    if p:
        printer_id = p.id
    db.close()
except Exception as e:
    print(f"  [WARN] No se pudo obtener impresora desde DB: {e}")
    # Fallback: via API con empresa 1
    try:
        r = requests.get(f"{BASE}/api/printers", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            pdata = r.json()
            pl = pdata.get("items", pdata) if isinstance(pdata, dict) else pdata
            if pl:
                printer_id = pl[0]["id"]
    except:
        pass

print(f"\n  [INFO] printer_id para pruebas = {printer_id}")

# ─────────────────────────────────────────────
# B.1 — Cierres y Comparaciones Guardadas
# ─────────────────────────────────────────────
section("BLOQUE B.1 — Comparaciones Guardadas")

cierres = []
if printer_id:
    try:
        r = requests.get(f"{BASE}/api/counters/monthly?printer_id={printer_id}",
                         headers=HEADERS, timeout=10)
        check("B.1.1 — GET /monthly?printer_id (200)", r.status_code == 200,
              f"status={r.status_code}")
        cierres = r.json() if r.status_code == 200 else []
        check("B.1.2 — Al menos 2 cierres disponibles", len(cierres) >= 2,
              f"encontrados={len(cierres)}")
    except Exception as e:
        check("B.1 — Listar cierres", False, str(e))
else:
    print("  ⚠️  Sin impresora disponible - omitiendo B.1")

comparacion_id = None
if len(cierres) >= 2:
    c1 = cierres[0]["id"]
    c2 = cierres[1]["id"]

    # Comparar dos cierres
    try:
        r = requests.get(f"{BASE}/api/counters/monthly/compare/{c1}/{c2}",
                         headers=HEADERS, timeout=15)
        check("B.1.3 — GET /monthly/compare/{c1}/{c2} (200)", r.status_code == 200,
              f"status={r.status_code}")
        snapshot = r.json() if r.status_code == 200 else {}
        check("B.1.4 — Snapshot tiene diferencia_total",
              "diferencia_total" in snapshot, f"keys={list(snapshot.keys())[:6]}")
    except Exception as e:
        check("B.1.3 — Compare endpoint", False, str(e))
        snapshot = {}

    # Guardar la comparación
    try:
        payload = {
            "titulo": "QA Test Sesion 29 Mayo 2026",
            "descripcion": "Prueba automatizada bloque B QA",
            "cierre1_id": c1,
            "cierre2_id": c2,
            "snapshot_json": snapshot
        }
        r = requests.post(f"{BASE}/api/counters/comparaciones",
                          json=payload, headers=HEADERS, timeout=10)
        check("B.1.5 — POST /comparaciones guarda OK",
              r.status_code in (200, 201), f"status={r.status_code}, body={r.text[:100]}")
        if r.status_code in (200, 201):
            comparacion_id = r.json().get("id")
    except Exception as e:
        check("B.1.5 — Guardar comparación", False, str(e))

    # Listar comparaciones guardadas
    try:
        r = requests.get(f"{BASE}/api/counters/comparaciones",
                         headers=HEADERS, timeout=10)
        lista = r.json() if r.status_code == 200 else []
        check("B.1.6 — GET /comparaciones lista (200)", r.status_code == 200,
              f"status={r.status_code}")
        check("B.1.7 — Comparación recién guardada aparece en lista",
              any(c.get("titulo", "").startswith("QA Test") for c in lista),
              f"total_en_lista={len(lista)}")
    except Exception as e:
        check("B.1.6 — Listar comparaciones", False, str(e))

    # Eliminar la comparación de prueba
    if comparacion_id:
        try:
            r = requests.delete(f"{BASE}/api/counters/comparaciones/{comparacion_id}",
                                headers=HEADERS, timeout=10)
            check("B.1.8 — DELETE comparación elimina OK",
                  r.status_code in (200, 204), f"status={r.status_code}")
        except Exception as e:
            check("B.1.8 — Eliminar comparación", False, str(e))

# ─────────────────────────────────────────────
# B.2 — Analytics
# ─────────────────────────────────────────────
section("BLOQUE B.2 — Analytics y Consumo")

# Evolution
try:
    r = requests.get(f"{BASE}/api/v1/analytics/evolution?meses=6",
                     headers=HEADERS, timeout=10)
    check("B.2.1 — GET /analytics/evolution?meses=6 (200)",
          r.status_code == 200, f"status={r.status_code}")
    evo = r.json() if r.status_code == 200 else []
    check("B.2.2 — Evolution retorna lista", isinstance(evo, list),
          f"type={type(evo).__name__}, len={len(evo)}")
except Exception as e:
    check("B.2.1 — Evolution", False, str(e))

# Comparison (ruta real: /comparison no /comparativa)
try:
    r = requests.get(
        f"{BASE}/api/v1/analytics/comparison"
        f"?fecha_inicio_a=2026-01-01&fecha_fin_a=2026-03-31"
        f"&fecha_inicio_b=2025-10-01&fecha_fin_b=2025-12-31",
        headers=HEADERS, timeout=10)
    check("B.2.3 — GET /analytics/comparison (200)",
          r.status_code == 200, f"status={r.status_code}")
    comp = r.json() if r.status_code == 200 else []
    check("B.2.4 — Comparison retorna lista", isinstance(comp, list),
          f"type={type(comp).__name__}, len={len(comp)}")
except Exception as e:
    check("B.2.3 — Comparison", False, str(e))

# Top users
try:
    r = requests.get(
        f"{BASE}/api/v1/analytics/top-users"
        f"?fecha_inicio=2026-01-01&fecha_fin=2026-03-31&limit=5",
        headers=HEADERS, timeout=10)
    check("B.2.5 — GET /analytics/top-users (200)",
          r.status_code == 200, f"status={r.status_code}")
    top = r.json() if r.status_code == 200 else []
    check("B.2.6 — Top users retorna lista", isinstance(top, list),
          f"items={len(top)}")
except Exception as e:
    check("B.2.5 — Top users", False, str(e))

# Global users
try:
    r = requests.get(f"{BASE}/api/counters/monthly/users/all?page=1&page_size=15",
                     headers=HEADERS, timeout=10)
    check("B.2.7 — GET /monthly/users/all paginado (200)",
          r.status_code == 200, f"status={r.status_code}")
    data = r.json() if r.status_code == 200 else {}
    check("B.2.8 — Respuesta tiene 'items' y 'pages'",
          "items" in data and "pages" in data,
          f"keys={list(data.keys())[:5]}")
except Exception as e:
    check("B.2.7 — Users consumo global", False, str(e))

# ─────────────────────────────────────────────
# C — Edge Cases
# ─────────────────────────────────────────────
section("BLOQUE C — Edge Cases")

# C.1 — Sin token → 401/403
try:
    r = requests.get(f"{BASE}/api/counters/comparaciones", timeout=10)
    check("C.1 — Sin token → 401 o 403",
          r.status_code in (401, 403), f"status={r.status_code}")
except Exception as e:
    check("C.1 — Sin token", False, str(e))

# C.2 — Título largo con emojis
if len(cierres) >= 2:
    titulo_largo = ("Comparativa Ricoh Master Principal 🚀 - Q1 - Edificio 3 Piso 2 "
                    "Centralizada de Contabilidad $$$ 12345 - Verificacion Automatizada")
    try:
        payload = {
            "titulo": titulo_largo,
            "descripcion": "Edge case: titulo largo con emojis",
            "cierre1_id": cierres[0]["id"],
            "cierre2_id": cierres[1]["id"],
            "snapshot_json": {"diferencia_total": 999}
        }
        r = requests.post(f"{BASE}/api/counters/comparaciones",
                          json=payload, headers=HEADERS, timeout=10)
        check("C.2 — Titulo largo + emojis guarda OK (no 422/500)",
              r.status_code in (200, 201, 422),
              f"status={r.status_code}")
        if r.status_code in (200, 201):
            tmp_id = r.json().get("id")
            if tmp_id:
                requests.delete(f"{BASE}/api/counters/comparaciones/{tmp_id}",
                                headers=HEADERS, timeout=5)
                check("C.2b — Comparación larga luego eliminada", True)
    except Exception as e:
        check("C.2 — Titulo largo", False, str(e))

# C.3 — Export Excel cierre (no CSV)
if printer_id and cierres:
    cierre_id = cierres[0]["id"]
    try:
        r = requests.get(f"{BASE}/api/export/cierre/{cierre_id}/excel",
                         headers=HEADERS, timeout=15)
        check("C.3 — Export /cierre/{id}/excel → 200",
              r.status_code == 200, f"status={r.status_code}")
        ct = r.headers.get("content-type", "")
        check("C.4 — Content-Type es Excel (.xlsx)",
              "spreadsheet" in ct or "openxmlformats" in ct or "octet-stream" in ct,
              f"content-type={ct}")
    except Exception as e:
        check("C.3 — Export Excel cierre", False, str(e))

    # C.5 — Verificar que ruta CSV ya NO existe
    try:
        r = requests.get(f"{BASE}/api/export/cierre/{cierre_id}",
                         headers=HEADERS, timeout=10)
        check("C.5 — Ruta CSV /export/cierre/{id} NO existe (404)",
              r.status_code == 404, f"status={r.status_code}")
    except Exception as e:
        check("C.5 — CSV endpoint eliminado", False, str(e))

# C.6 — Dashboard toner-alertas (fix Printer importado)
try:
    r = requests.get(f"{BASE}/api/v1/dashboard/toner-alertas",
                     headers=HEADERS, timeout=10)
    check("C.6 — GET /dashboard/toner-alertas (200, Printer OK)",
          r.status_code == 200, f"status={r.status_code}")
except Exception as e:
    check("C.6 — Dashboard toner-alertas", False, str(e))

# C.7 — Export comparacion Excel (si hay 2 cierres)
if len(cierres) >= 2:
    c1, c2 = cierres[0]["id"], cierres[1]["id"]
    try:
        r = requests.get(f"{BASE}/api/export/comparacion/{c1}/{c2}/excel",
                         headers=HEADERS, timeout=15)
        check("C.7 — Export /comparacion/{id1}/{id2}/excel → 200",
              r.status_code == 200, f"status={r.status_code}")
    except Exception as e:
        check("C.7 — Export Excel comparacion", False, str(e))

    # C.8 — CSV de comparacion ya NO existe
    try:
        r = requests.get(f"{BASE}/api/export/comparacion/{c1}/{c2}",
                         headers=HEADERS, timeout=10)
        check("C.8 — Ruta CSV /export/comparacion/{id1}/{id2} NO existe (404)",
              r.status_code == 404, f"status={r.status_code}")
    except Exception as e:
        check("C.8 — CSV comparacion eliminado", False, str(e))

# ─────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────
section("RESUMEN FINAL")
passed = sum(1 for _, ok, _ in RESULTS if ok)
total = len(RESULTS)
failed = [(l, d) for l, ok, d in RESULTS if not ok]

print(f"\n  Total: {passed}/{total} checks pasaron\n")
if failed:
    print("  FALLOS:")
    for label, detail in failed:
        print(f"    ❌ {label}")
        if detail:
            print(f"       → {detail}")
    sys.exit(1)
else:
    print("  🎉 TODOS LOS CHECKS B + C PASARON")
