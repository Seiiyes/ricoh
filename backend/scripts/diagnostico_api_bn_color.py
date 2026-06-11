"""
Diagnóstico B/N y Color en comparación de cierres.
Usa la API HTTP directamente para verificar los datos que llegan.
Ejecutar desde: backend/
  python scripts/diagnostico_api_bn_color.py
"""
import urllib.request
import urllib.error
import json
import sys

BASE = "http://localhost:8000"

def req(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=15)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body_err = json.loads(e.read().decode())
        except Exception:
            body_err = {}
        return e.code, body_err
    except Exception as ex:
        return 0, {"error": str(ex)}

def fmt(n):
    try:
        return f"{int(n):>12,}"
    except Exception:
        return f"{'N/A':>12}"

print("\n" + "="*80)
print("  DIAGNÓSTICO: DATOS B/N y COLOR EN COMPARACIÓN DE CIERRES")
print("="*80)

# ── 1. Login ──────────────────────────────────────────────────────────────────
print("\n[1] Login como superadmin...")
status, body = req("POST", "/auth/login", {"username": "superadmin", "password": "Admin1234!"})
token = body.get("access_token", "")
if status != 200 or not token:
    print(f"  ❌ Login falló (status={status}). Revisa la contraseña del superadmin.")
    sys.exit(1)
print(f"  ✅ Login OK")

# ── 2. Obtener impresoras ─────────────────────────────────────────────────────
print("\n[2] Obteniendo impresoras...")
status, resp = req("GET", "/printers/", token=token)
printers = resp.get("items", []) if isinstance(resp, dict) else (resp if isinstance(resp, list) else [])
if not printers:
    print(f"  ❌ No se encontraron impresoras (status={status})")
    sys.exit(1)
print(f"  ✅ {len(printers)} impresoras encontradas")

# ── 3. Para cada impresora, obtener cierres y comparar ───────────────────────
print("\n[3] Analizando por impresora...\n")

for printer in printers:
    pid = printer.get("id")
    hostname = printer.get("hostname", f"printer_{pid}")
    has_color = printer.get("has_color", False)

    status, cierres = req("GET", f"/api/counters/monthly?printer_id={pid}", token=token)
    cierres = cierres if isinstance(cierres, list) else []

    if len(cierres) < 2:
        print(f"  ⚠️  [{pid}] {hostname} — solo {len(cierres)} cierre(s), se necesitan ≥2. SALTANDO.")
        continue

    # Tomar el más antiguo y el más reciente
    cierres_ord = sorted(cierres, key=lambda c: c.get("fecha_inicio",""))
    c1 = cierres_ord[0]
    c2 = cierres_ord[-1]
    c1_id, c2_id = c1["id"], c2["id"]

    print(f"{'─'*78}")
    print(f"  [{pid}] {hostname}")
    print(f"       has_color = {has_color}")
    print(f"       Cierre BASE    : [{c1_id}]  {c1.get('fecha_inicio')} → {c1.get('fecha_fin')}")
    print(f"       Cierre RECIENTE: [{c2_id}]  {c2.get('fecha_inicio')} → {c2.get('fecha_fin')}")

    # Llamar a la API de comparación
    status, comp = req("GET", f"/api/counters/monthly/compare/{c1_id}/{c2_id}", token=token)
    if status != 200:
        print(f"       ❌ Error al comparar (status={status}): {comp}")
        continue

    # ── Verificar campos nuevos en el nivel raíz ──────────────────────────────
    print(f"\n       📊 CAMPOS EN RAÍZ DE LA RESPUESTA:")
    diferencia_total  = comp.get("diferencia_total", "MISSING")
    diferencia_bn     = comp.get("diferencia_bn",    "MISSING")
    diferencia_color  = comp.get("diferencia_color", "MISSING")
    diferencia_cop    = comp.get("diferencia_copiadora", "?")
    diferencia_imp    = comp.get("diferencia_impresora", "?")
    diferencia_esc    = comp.get("diferencia_escaner", "?")

    ok_bn    = diferencia_bn    != "MISSING"
    ok_color = diferencia_color != "MISSING"

    print(f"         diferencia_total     = {fmt(diferencia_total)}")
    print(f"         diferencia_bn        = {fmt(diferencia_bn)}  {'✅' if ok_bn else '❌ CAMPO FALTANTE'}")
    print(f"         diferencia_color     = {fmt(diferencia_color)}  {'✅' if ok_color else '❌ CAMPO FALTANTE'}")
    print(f"         diferencia_copiadora = {fmt(diferencia_cop)}")
    print(f"         diferencia_impresora = {fmt(diferencia_imp)}")
    print(f"         diferencia_escaner   = {fmt(diferencia_esc)}")

    # ── Verificar coherencia B/N+Color vs Total ───────────────────────────────
    if ok_bn and ok_color and isinstance(diferencia_bn, int) and isinstance(diferencia_color, int):
        suma_bn_color = diferencia_bn + diferencia_color
        diff_real = comp.get("diferencia_total", 0)
        pct_diff = abs(suma_bn_color - diff_real) / max(abs(diff_real), 1) * 100
        if pct_diff < 20:
            print(f"\n         ✅ Coherencia: B/N({diferencia_bn:,}) + Color({diferencia_color:,}) = {suma_bn_color:,}  ≈ Total({diff_real:,})  (Δ{pct_diff:.1f}%)")
        else:
            print(f"\n         ⚠️  Baja coherencia: B/N+Color={suma_bn_color:,} vs Total={diff_real:,}  (Δ{pct_diff:.1f}%)")
            print(f"            Esto puede ser normal si total_bn/color en BD son contadores acumulados distintos al diferencial total.")

    # ── Verificar campos B/N/Color en usuarios individuales ──────────────────
    todos_usuarios = comp.get("top_usuarios_aumento", []) + comp.get("top_usuarios_disminucion", [])
    print(f"\n       👥 USUARIOS EN RESPUESTA: {len(todos_usuarios)} usuarios")

    if todos_usuarios:
        # Verificar que los campos clave existen
        u = todos_usuarios[0]
        campos_requeridos = [
            "copiadora_bn_cierre1", "copiadora_color_cierre1",
            "impresora_bn_cierre1", "impresora_color_cierre1",
            "copiadora_bn_cierre2", "copiadora_color_cierre2",
            "impresora_bn_cierre2", "impresora_color_cierre2",
        ]
        campos_ok = all(k in u for k in campos_requeridos)
        print(f"         Campos B/N y Color presentes en usuarios: {'✅ SÍ' if campos_ok else '❌ FALTAN CAMPOS'}")
        if not campos_ok:
            faltan = [k for k in campos_requeridos if k not in u]
            print(f"         Campos faltantes: {faltan}")

        # Mostrar 3 usuarios de muestra
        print(f"\n         Muestra (primeros 3 usuarios con diferencia != 0):")
        print(f"         {'Nombre':<22}  {'cop_bn1':>7}  {'cop_col1':>9}  {'cop_bn2':>7}  {'cop_col2':>9}  {'dif_bn(calc)':>12}  {'dif_col(calc)':>13}")
        muestra = [u for u in todos_usuarios if u.get("diferencia", 0) != 0][:3] or todos_usuarios[:3]
        for u in muestra:
            cb1 = u.get("copiadora_bn_cierre1", 0) or 0
            cc1 = u.get("copiadora_color_cierre1", 0) or 0
            ib1 = u.get("impresora_bn_cierre1", 0) or 0
            ic1 = u.get("impresora_color_cierre1", 0) or 0
            cb2 = u.get("copiadora_bn_cierre2", 0) or 0
            cc2 = u.get("copiadora_color_cierre2", 0) or 0
            ib2 = u.get("impresora_bn_cierre2", 0) or 0
            ic2 = u.get("impresora_color_cierre2", 0) or 0
            dif_bn_calc = (cb2 + ib2) - (cb1 + ib1)
            dif_color_calc = (cc2 + ic2) - (cc1 + ic1)
            nombre = u.get("nombre_usuario", "?")[:22]
            print(f"         {nombre:<22}  {cb1:>7,}  {cc1:>9,}  {cb2:>7,}  {cc2:>9,}  {dif_bn_calc:>+12,}  {dif_color_calc:>+13,}")

        # Verificar has_color vs datos reales
        total_color_vals = sum(
            (u.get("copiadora_color_cierre2") or 0) + (u.get("impresora_color_cierre2") or 0)
            for u in todos_usuarios
        )
        print(f"\n         Suma total de valores 'color' en cierre2 de todos los usuarios: {total_color_vals:,}")
        if has_color and total_color_vals == 0:
            print(f"         ⚠️  has_color=True pero TODOS los valores color son 0 → impresora puede ser realmente B/N o datos no registrados")
        elif not has_color and total_color_vals > 0:
            print(f"         ⚠️  has_color=False pero hay datos de color → revisar has_color en BD para esta impresora")
        else:
            print(f"         ✅ Consistente con has_color={has_color}")

print("\n" + "="*80)
print("  FIN DEL DIAGNÓSTICO")
print("="*80 + "\n")
