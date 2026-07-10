#!/usr/bin/env python3
"""
Diagnóstico COMPLETO con auth correcta (login.cgi + base64).
Lista trabajos de JUANL y prueba eliminar UNO con distintos typeOnly.
"""
import sys
import os
import requests
import base64
import re
import time
from bs4 import BeautifulSoup

PRINTER_IP = "192.168.91.251"
ADMIN_USER = "admin"
ADMIN_PASSWORD = ""
TARGET_USER = "JUANL"

BASE_URL = f"http://{PRINTER_IP}"
OUT_DIR = "C:/Users/juan.lizarazo/Desktop/ricoh"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
})
session.cookies.set('cookieOnOffChecker', 'on', path='/')


def save(name, txt):
    p = f"{OUT_DIR}/{name}"
    with open(p, 'w', encoding='utf-8', errors='replace') as f:
        f.write(txt)
    print(f"  [guardado] {name}  ({len(txt)} chars)")

def pline(s):
    print(s.encode('ascii', errors='replace').decode())

pline("=" * 70)
pline(f"DIAGNOSTICO — Impresora {PRINTER_IP}")
pline("=" * 70)

# ── 1. GET authForm para obtener wimToken de login ──────────────────────
pline("\n[1] Obteniendo wimToken de authForm.cgi...")
form_url = f"{BASE_URL}/web/guest/es/websys/webArch/authForm.cgi"
r_form = session.get(form_url, timeout=15)
pline(f"  Status: {r_form.status_code}")
save("diag_01_authForm.html", r_form.text)

token_match = re.search(r'name="wimToken"\s+value="(\d+)"', r_form.text)
login_token = token_match.group(1) if token_match else ""
pline(f"  wimToken de login: {login_token!r}")

# ── 2. POST login.cgi con userid en base64 ───────────────────────────────
pline("\n[2] Login via login.cgi (userid en base64)...")
login_url = f"{BASE_URL}/web/guest/es/websys/webArch/login.cgi"
userid_b64 = base64.b64encode(ADMIN_USER.encode()).decode()
login_data = {
    'wimToken': login_token,
    'userid_work': '',
    'userid': userid_b64,
    'password_work': '',
    'password': ADMIN_PASSWORD,
    'open': '',
}
pline(f"  userid (b64): {userid_b64}  pass: {ADMIN_PASSWORD}")

r_login = session.post(login_url, data=login_data, timeout=15, allow_redirects=True)
pline(f"  Status: {r_login.status_code}  URL: {r_login.url}")
save("diag_02_login.html", r_login.text)

# Verificar si login fue exitoso (buscar wimToken en la respuesta)
if 'wimToken' not in r_login.text and 'logout' not in r_login.text.lower():
    pline("  ADVERTENCIA: login puede haber fallado")

# ── 3. GET storedJob.cgi ────────────────────────────────────────────────
pline("\n[3] GET storedJob.cgi (ruta entry)...")
stored_url = f"{BASE_URL}/web/entry/es/webprinter/storedJob.cgi"
r_jobs = session.get(stored_url, timeout=15, headers={
    'Referer': f'{BASE_URL}/web/entry/es/websys/webArch/topPage.cgi'
})
pline(f"  Status: {r_jobs.status_code}  Size: {len(r_jobs.text)}")
save("diag_03_storedJobs.html", r_jobs.text)

soup = BeautifulSoup(r_jobs.text, 'html.parser')

# Extraer campos
wim_token  = (soup.find('input', {'name': 'wimToken'}) or {}).get('value', '')
base_id    = (soup.find('input', {'name': 'baseID'}) or {}).get('value', '')
total_count= (soup.find('input', {'name': 'totalCount'}) or {}).get('value', '100')
size_val   = (soup.find('input', {'name': 'size'}) or {}).get('value', '10')
display_ids= [el.get('value','') for el in soup.find_all('input', {'name': 'display_ID'})]
all_ids    = [el.get('value','') for el in soup.find_all('input', {'name': 'ID'})]

pline(f"\n  wimToken    = {wim_token!r}")
pline(f"  baseID      = {base_id!r}")
pline(f"  totalCount  = {total_count!r}  size = {size_val!r}")
pline(f"  display_IDs = {display_ids}")
pline(f"  All IDs     = {all_ids}")

pline("\n  --- Todos los inputs ---")
for inp in soup.find_all('input'):
    pline(f"    [{inp.get('type','text'):8s}] {inp.get('name',''):22s} = {str(inp.get('value',''))[:60]!r}")

# Extraer trabajos de la tabla
pline("\n  --- Tabla de trabajos ---")
juanl_jobs = []
table = soup.find('table', class_='reportListCommon')
if table:
    for row in table.find_all('tr'):
        cells = row.find_all('td', class_='listData')
        if len(cells) >= 8:
            # Checkbox / Job ID
            id_el = cells[0].find('input', {'name': 'ID'})
            if not id_el:
                id_el = cells[0].find('input', type='hidden')
            jid   = id_el.get('value','') if id_el else ''

            tipo = cells[1].get_text(strip=True)
            user = cells[3].get_text(strip=True)
            name = cells[4].get_text(strip=True)
            pline(f"    ID={jid:6s}  User={user:15s}  Type={tipo[:25]:25s}  Doc={name[:40]}")
            if TARGET_USER.upper() in user.upper():
                juanl_jobs.append({'id': jid, 'name': name, 'type': tipo})

else:
    pline("  tabla 'reportListCommon' NO encontrada. Buscando otras tablas...")
    for t in soup.find_all('table')[:5]:
        pline(f"    tabla class={t.get('class',[])}  rows={len(t.find_all('tr'))}")

pline(f"\n  Trabajos de {TARGET_USER}: {juanl_jobs}")

if not juanl_jobs:
    pline(f"\n  No hay trabajos de {TARGET_USER}. Fin.")
    sys.exit(0)

# ── 4. Intentar eliminar el PRIMER trabajo de JUANL ─────────────────────
job = juanl_jobs[0]
job_id = job['id']
pline(f"\n[4] Intentando eliminar ID={job_id}  ({job['name']!r})")

for type_only in ['-1', '3', '2']:
    # Refrescar wimToken
    r_ref = session.get(stored_url, timeout=15, headers={'Referer': f'{BASE_URL}/web/entry/es/websys/webArch/topPage.cgi'})
    s_ref = BeautifulSoup(r_ref.text, 'html.parser')
    wt   = (s_ref.find('input', {'name': 'wimToken'}) or {}).get('value', wim_token)
    dids = [el.get('value','') for el in s_ref.find_all('input', {'name': 'display_ID'})]

    payload = [
        ('wimToken', wt), ('notDefault', '1'), ('mode', '1'), ('exec', '2'),
        ('baseID', base_id), ('position', ''), ('size', size_val), ('Copies', '0'),
        ('totalCount', total_count), ('selectedType', '-1'), ('typeExisted', '1'),
        ('typeOnly', type_only), ('targetID', '-1'), ('view', '0'),
        ('selectedUserID', ''), ('number', '10'), ('selectedCount', '1'),
    ]
    for d in dids:
        payload.append(('display_ID', d))
    payload.append(('ID', job_id))

    pline(f"\n  typeOnly={type_only}  wimToken={wt!r}  display_IDs={dids}")
    pline(f"  payload: {payload}")

    # ── Step A: Send first delete request (GETs the confirmation page) ──
    post_r = session.post(stored_url, data=payload, timeout=15, headers={
        'Referer': stored_url, 'Content-Type': 'application/x-www-form-urlencoded', 'Origin': BASE_URL,
    })
    pline(f"  First POST status: {post_r.status_code}")
    save(f"diag_04_POST_typeOnly{type_only}.html", post_r.text)

    # ── Step B: Parse confirmation page (hideform) and send the second POST (Exec) ──
    confirm_soup = BeautifulSoup(post_r.text, 'html.parser')
    confirm_form = confirm_soup.find('form', {'name': 'hideform'})
    if not confirm_form:
        pline("  ❌ ERROR: No se encontro el formulario 'hideform' de confirmacion en la respuesta!")
        continue

    confirm_payload = []
    for inp in confirm_form.find_all('input'):
        iname = inp.get('name', '')
        ivalue = inp.get('value', '')
        if iname:
            if iname == 'mode':
                confirm_payload.append((iname, '3')) # Exec() sets mode to 3
            else:
                confirm_payload.append((iname, ivalue))

    pline(f"  Sending confirmation POST with mode=3...")
    pline(f"  Confirmation payload: {confirm_payload}")

    confirm_r = session.post(stored_url, data=confirm_payload, timeout=15, headers={
        'Referer': stored_url, 'Content-Type': 'application/x-www-form-urlencoded', 'Origin': BASE_URL,
    })
    pline(f"  Confirmation POST status: {confirm_r.status_code}")
    save(f"diag_04_confirm_response_typeOnly{type_only}.html", confirm_r.text)

    # ── Step C: Verify deletion ──
    time.sleep(2)
    verify_r = session.get(stored_url, timeout=15, headers={'Referer': f'{BASE_URL}/web/entry/es/websys/webArch/topPage.cgi'})
    save(f"diag_05_verify_typeOnly{type_only}.html", verify_r.text)
    vs = BeautifulSoup(verify_r.text, 'html.parser')
    remaining = [el.get('value','') for el in vs.find_all('input', {'name': 'ID'})]
    pline(f"  IDs restantes en GET de verificacion: {remaining}")
    if job_id in remaining:
        pline(f"  FALLO: Job {job_id} SIGUE con typeOnly={type_only}")
    else:
        pline(f"  EXITO: Job {job_id} YA NO aparece con typeOnly={type_only} — ELIMINADO!")
        break


pline("\n" + "=" * 70)
pline("Fin diagnostico. Revisa archivos diag_*.html en el Desktop/ricoh.")
