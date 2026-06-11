"""
Script de Cargue Masivo de Empresa y Área (Centro de Costo) desde Excel
========================================================================
Archivo fuente: docs/USUARIOS IMPRESORA.xlsx
Columnas usadas: Usuario (código), EMPRESA, AREA
Columna ignorada: B/N (datos históricos de consumo, no relevantes para el cargue)

Lógica:
  - Limpia corchetes y espacios del código de usuario para hacer match con la BD.
  - Para cada (código_usuario, empresa), asigna empresa_id y centro_costo_id al usuario.
  - Si la empresa no existe en la BD, la crea automáticamente.
  - Si el centro de costo (área) no existe para esa empresa, lo crea.
  - Si el mismo código aparece múltiples veces con la misma empresa, toma el área del
    primer registro sin duplicados (todos deberían tener la misma área).
  - Genera un reporte de qué usuarios no se encontraron en la BD.

Uso:
  python backend/scripts/cargue_masivo_empresa_usuarios.py

Requisitos:
  - pip install openpyxl psycopg2-binary
  - Variables de entorno: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    (o configurar directamente en las constantes al inicio del script)
"""

import os
import re
import json
import openpyxl
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE BASE DE DATOS
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "ricoh_fleet"),
    "user":     os.getenv("DB_USER",     "ricoh_admin"),
    "password": os.getenv("DB_PASSWORD", "ricoh_secure_2024"),
}

# ─────────────────────────────────────────────
# RUTA DEL EXCEL
# ─────────────────────────────────────────────
EXCEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "docs", "USUARIOS IMPRESORA.xlsx"
)

# ─────────────────────────────────────────────
# MODO SIMULACIÓN (True = solo muestra, no escribe en BD)
# ─────────────────────────────────────────────
DRY_RUN = False  # Cambiar a True para probar sin modificar la BD


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def limpiar_codigo(valor: str) -> str:
    """Elimina corchetes, espacios y normaliza el código de usuario."""
    if not valor:
        return ""
    # Quitar corchetes [], espacios al inicio/final y paréntesis
    limpio = re.sub(r"[\[\]\(\)]", "", str(valor)).strip()
    return limpio


def normalizar_nombre(valor: str) -> str:
    """Normaliza mayúsculas y elimina espacios extra."""
    if not valor:
        return ""
    return " ".join(str(valor).upper().strip().split())


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ─────────────────────────────────────────────
# PASO 1: Leer y deduplicar el Excel
# ─────────────────────────────────────────────
def leer_excel(path: str) -> list[dict]:
    """
    Lee el Excel y retorna registros únicos por (codigo, empresa).
    Columnas usadas: Usuario, EMPRESA, AREA
    Columna B/N ignorada.
    """
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    headers = rows[0]
    log(f"Excel: {len(rows)-1} filas brutas, columnas: {headers}")

    # Mapa de deduplicación: (codigo_limpio, empresa_normalizada) -> area
    dedup: dict[tuple, dict] = {}

    for fila in rows[1:]:
        if not fila[1] or not fila[3]:  # Usuario y EMPRESA son obligatorios
            continue

        codigo_raw  = str(fila[1]).strip()
        nombre_raw  = str(fila[2]).strip() if fila[2] else ""
        empresa_raw = str(fila[3]).strip()
        area_raw    = str(fila[4]).strip() if fila[4] else ""

        codigo   = limpiar_codigo(codigo_raw)
        empresa  = normalizar_nombre(empresa_raw)
        area     = normalizar_nombre(area_raw)

        # Nombre limpio: preferir el que no tiene corchetes
        nombre_limpio = normalizar_nombre(re.sub(r"[\[\]\(\)]", "", nombre_raw).strip())

        key = (codigo, empresa)
        if key not in dedup:
            dedup[key] = {
                "codigo":  codigo,
                "nombre":  nombre_limpio,
                "empresa": empresa,
                "area":    area,
            }
        else:
            # Si el área es la misma, no hay conflicto. Si difiere, mantener la primera.
            if dedup[key]["area"] != area and area:
                log(f"  ⚠️  Código {codigo} ({empresa}): área múltiple → "
                    f"'{dedup[key]['area']}' vs '{area}' — se mantiene la primera.")

    log(f"Registros únicos (codigo, empresa): {len(dedup)}")
    return list(dedup.values())


# ─────────────────────────────────────────────
# PASO 2: Obtener o crear empresa
# ─────────────────────────────────────────────
def obtener_o_crear_empresa(cur, nombre_excel: str, cache: dict) -> int | None:
    """
    Busca la empresa por nombre_comercial (case-insensitive) o razon_social.
    Si no existe y DRY_RUN=False, la crea con datos mínimos.
    Usa un cache en memoria para evitar queries repetidas.
    """
    nombre_norm = nombre_excel.lower().strip()

    if nombre_norm in cache:
        return cache[nombre_norm]

    cur.execute(
        """
        SELECT id FROM empresas
        WHERE LOWER(nombre_comercial) = %s OR LOWER(razon_social) = %s
        """,
        (nombre_norm, nombre_norm),
    )
    row = cur.fetchone()
    if row:
        cache[nombre_norm] = row["id"]
        log(f"  ✅ Empresa encontrada: '{nombre_excel}' → id={row['id']}")
        return row["id"]

    # No existe → crear
    if DRY_RUN:
        log(f"  🔵 [DRY_RUN] Crearía empresa: '{nombre_excel}'")
        cache[nombre_norm] = -1  # sentinel para dry-run
        return -1

    cur.execute(
        """
        INSERT INTO empresas (razon_social, nombre_comercial, config_json, is_active)
        VALUES (%s, %s, %s, TRUE)
        RETURNING id
        """,
        (
            nombre_excel.upper(),
            nombre_excel.lower(),
            json.dumps({}),
        ),
    )
    nuevo_id = cur.fetchone()["id"]
    cache[nombre_norm] = nuevo_id
    log(f"  🆕 Empresa CREADA: '{nombre_excel}' → id={nuevo_id}")
    return nuevo_id


# ─────────────────────────────────────────────
# PASO 3: Obtener o crear centro de costo
# ─────────────────────────────────────────────
def obtener_o_crear_centro_costo(cur, empresa_id: int, area: str, cache: dict) -> int | None:
    """
    Busca el centro de costo por nombre + empresa_id.
    Si no existe, lo crea. Usa cache en memoria.
    """
    if not area:
        return None

    key = (empresa_id, area.lower())
    if key in cache:
        return cache[key]

    cur.execute(
        """
        SELECT id FROM centro_costos
        WHERE empresa_id = %s AND LOWER(nombre) = %s
        """,
        (empresa_id, area.lower()),
    )
    row = cur.fetchone()
    if row:
        cache[key] = row["id"]
        return row["id"]

    # No existe → crear
    if DRY_RUN:
        log(f"    🔵 [DRY_RUN] Crearía centro de costo: '{area}' para empresa_id={empresa_id}")
        cache[key] = -1
        return -1

    cur.execute(
        """
        INSERT INTO centro_costos (nombre, empresa_id)
        VALUES (%s, %s)
        RETURNING id
        """,
        (area.upper(), empresa_id),
    )
    nuevo_id = cur.fetchone()["id"]
    cache[key] = nuevo_id
    log(f"    🆕 Centro de costo CREADO: '{area}' → id={nuevo_id} (empresa_id={empresa_id})")
    return nuevo_id


# ─────────────────────────────────────────────
# PASO 4: Buscar usuario en la BD
# ─────────────────────────────────────────────
def buscar_usuario(cur, codigo: str) -> list[dict]:
    """Busca usuarios por código exacto. Puede haber más de uno con el mismo código."""
    cur.execute(
        """
        SELECT id, name, codigo_de_usuario, empresa_id, centro_costo_id
        FROM users
        WHERE codigo_de_usuario = %s
        """,
        (codigo,),
    )
    return cur.fetchall()


# ─────────────────────────────────────────────
# PASO 5: Actualizar usuario
# ─────────────────────────────────────────────
def actualizar_usuario(cur, user_id: int, empresa_id: int, centro_costo_id: int | None):
    """Asigna empresa_id y centro_costo_id al usuario."""
    if DRY_RUN:
        return
    cur.execute(
        """
        UPDATE users
        SET empresa_id = %s, centro_costo_id = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (empresa_id, centro_costo_id, user_id),
    )


# ─────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ─────────────────────────────────────────────
def main():
    log("=" * 60)
    log("CARGUE MASIVO: EMPRESA Y ÁREA DE USUARIOS")
    log(f"Modo: {'🔵 SIMULACIÓN (DRY_RUN)' if DRY_RUN else '🟢 ESCRITURA REAL'}")
    log("=" * 60)

    # Leer Excel
    registros = leer_excel(os.path.abspath(EXCEL_PATH))

    # Conectar a BD
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    conn.autocommit = False
    cur = conn.cursor()

    empresa_cache:      dict = {}  # nombre → id
    cc_cache:           dict = {}  # (empresa_id, area) → id
    no_encontrados:     list = []
    actualizados:       int  = 0
    ya_tenia_empresa:   int  = 0
    errores:            int  = 0

    try:
        for reg in registros:
            codigo   = reg["codigo"]
            empresa  = reg["empresa"]
            area     = reg["area"]

            # 1. Resolver empresa
            empresa_id = obtener_o_crear_empresa(cur, empresa, empresa_cache)
            if empresa_id is None:
                log(f"  ❌ No se pudo resolver empresa '{empresa}' para código {codigo}")
                errores += 1
                continue

            # 2. Resolver centro de costo
            cc_id = None
            if area and empresa_id != -1:  # -1 = dry-run sentinel
                cc_id = obtener_o_crear_centro_costo(cur, empresa_id, area, cc_cache)

            # 3. Buscar usuario en BD
            usuarios_bd = buscar_usuario(cur, codigo)
            if not usuarios_bd:
                no_encontrados.append({
                    "codigo":  codigo,
                    "nombre":  reg["nombre"],
                    "empresa": empresa,
                    "area":    area,
                })
                log(f"  ⚠️  Código {codigo} ({reg['nombre']}) NO encontrado en la BD")
                continue

            # 4. Actualizar todos los usuarios con ese código
            for u in usuarios_bd:
                if u["empresa_id"] is not None and u["empresa_id"] != empresa_id:
                    log(f"  ⚠️  Usuario id={u['id']} ({u['name']}) ya tiene empresa_id={u['empresa_id']}, "
                        f"sobreescribiendo con {empresa_id} ({empresa})")
                    ya_tenia_empresa += 1

                if DRY_RUN:
                    log(f"  🔵 [DRY_RUN] Actualizaría usuario id={u['id']} ({u['name']}) "
                        f"→ empresa_id={empresa_id}, centro_costo_id={cc_id}, area='{area}'")
                else:
                    actualizar_usuario(cur, u["id"], empresa_id, cc_id)
                    log(f"  ✅ Usuario id={u['id']} ({u['name']}) → empresa='{empresa}', área='{area}'")
                actualizados += 1

        if not DRY_RUN:
            conn.commit()
            log("\n✅ COMMIT realizado correctamente.")
        else:
            conn.rollback()
            log("\n🔵 DRY_RUN: ningún cambio fue persistido.")

    except Exception as e:
        conn.rollback()
        log(f"\n❌ ERROR: {e}")
        raise
    finally:
        cur.close()
        conn.close()

    # ─── REPORTE FINAL ───
    log("\n" + "=" * 60)
    log("REPORTE FINAL")
    log("=" * 60)
    log(f"  Registros únicos procesados:  {len(registros)}")
    log(f"  Usuarios actualizados:        {actualizados}")
    log(f"  Ya tenían empresa distinta:   {ya_tenia_empresa}")
    log(f"  Errores de procesamiento:     {errores}")
    log(f"  NO encontrados en BD:         {len(no_encontrados)}")

    if no_encontrados:
        log("\n⚠️  USUARIOS NO ENCONTRADOS EN LA BASE DE DATOS:")
        log(f"  {'Código':<10} {'Nombre':<25} {'Empresa':<25} {'Área'}")
        log(f"  {'-'*10} {'-'*25} {'-'*25} {'-'*20}")
        for u in no_encontrados:
            log(f"  {u['codigo']:<10} {u['nombre']:<25} {u['empresa']:<25} {u['area']}")


if __name__ == "__main__":
    main()
