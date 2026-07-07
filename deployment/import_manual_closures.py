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

print("Creating import script with real physical machine general counters...")

# Script de importación de Python que se ejecutará dentro del contenedor ricoh-backend
import_python_code = """
cat << 'EOF' > /tmp/import_june_closures.py
import os
import csv
import re
from datetime import date, datetime
import sys
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import CierreMensual, CierreMensualUsuario, Printer, User, UserPrinterAssignment
from db.database import SessionLocal

def limpiar_string(val):
    if not val:
        return ""
    return re.sub(r"[\\'\\[\\]\\\"\\(\\)]", "", str(val)).strip()

def parse_int(val):
    if not val or val == "-" or val == "---":
        return 0
    try:
        val_clean = str(val).replace(",", "").replace(".", "").strip()
        return int(val_clean)
    except:
        return 0

# Contadores generales extraídos de las capturas de pantalla de WhatsApp del 19.06.2026
general_counters = {
    "E174M210096": {
        "total_paginas": 521916,
        "total_copiadora": 86190,
        "total_impresora": 435062,
        "total_escaner": 125415,
        "total_fax": 664
    },
    "E174MA11130": {
        "total_paginas": 453731,
        "total_copiadora": 80108,
        "total_impresora": 373577,
        "total_escaner": 210720,
        "total_fax": 46
    },
    "E176M460020": {
        "total_paginas": 994377,
        "total_copiadora": 318625,
        "total_impresora": 675752,
        "total_escaner": 199360,
        "total_fax": 0
    },
    "G986XA16285": {
        "total_paginas": 293805,
        "total_copiadora": 98452,
        "total_impresora": 195353,
        "total_escaner": 50899,
        "total_fax": 0
    },
    "W533L900719": {
        "total_paginas": 1080927,
        "total_copiadora": 120265,
        "total_impresora": 960662,
        "total_escaner": 161749,
        "total_fax": 0
    }
}

def import_csv_for_printer(db, filepath, serial):
    print(f"\\nProcessing CSV file {filepath} for serial {serial}...")
    
    # 1. Obtener la impresora en DB
    printer = db.query(Printer).filter(Printer.serial_number == serial).first()
    if not printer:
        print(f"   ❌ Error: Printer with serial {serial} not found in database!")
        return False
        
    print(f"   ✓ Printer found: {printer.hostname} (ID: {printer.id}, Location: {printer.location})")
    
    # 2. Eliminar si ya existe un cierre para Junio 19 de esta impresora
    cierre_existente = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer.id,
        CierreMensual.fecha_fin == date(2026, 6, 19)
    ).first()
    if cierre_existente:
        print(f"   🧹 Removing existing duplicate closure (ID: {cierre_existente.id}) for this date...")
        db.delete(cierre_existente)
        db.commit()
    
    # 3. Buscar si ya existe un cierre previo de esta impresora
    ultimo_cierre = db.query(CierreMensual).filter(
        CierreMensual.printer_id == printer.id,
        CierreMensual.fecha_fin < date(2026, 6, 19)
    ).order_by(CierreMensual.fecha_fin.desc()).first()
    
    lecturas_anteriores = {}
    if ultimo_cierre:
        print(f"   ✓ Previous closure found: ID {ultimo_cierre.id} on {ultimo_cierre.fecha_fin} ({ultimo_cierre.total_paginas} pages)")
        for u_cierre in ultimo_cierre.usuarios:
            lecturas_anteriores[u_cierre.user_id] = {
                "total_paginas": u_cierre.total_paginas,
                "copiadora_bn": u_cierre.copiadora_bn,
                "copiadora_color": u_cierre.copiadora_color,
                "impresora_bn": u_cierre.impresora_bn,
                "impresora_color": u_cierre.impresora_color,
                "escaner_bn": u_cierre.escaner_bn,
                "escaner_color": u_cierre.escaner_color,
                "fax_bn": u_cierre.fax_bn
            }
    else:
        print("   ⚠️ No previous closures found for this printer. Consumptions will be set to 0.")

    # 4. Leer y parsear el CSV
    usuarios_cierre = []
    
    # Obtener contadores generales reales de las capturas de pantalla de la máquina
    real_cnt = general_counters.get(serial, {})
    total_paginas_impresora = real_cnt.get("total_paginas", 0)
    total_copiadora_impresora = real_cnt.get("total_copiadora", 0)
    total_impresora_impresora = real_cnt.get("total_impresora", 0)
    total_escaner_impresora = real_cnt.get("total_escaner", 0)
    total_fax_impresora = real_cnt.get("total_fax", 0)

    with open(filepath, mode='r', encoding='utf-8') as csv_file:
        first_line = csv_file.readline()
        csv_file.seek(0)
        
        is_ecologico = "Código de usuario" in first_line or "Nº de registro" in first_line
        print(f"   ℹ️ Detected format: {'ECOLOGICO' if is_ecologico else 'ESTANDAR'}")
        
        reader = csv.DictReader(csv_file)
        
        for row in reader:
            if is_ecologico:
                raw_user_code = row.get('Código de usuario') or row.get('código de usuario')
                user_code = limpiar_string(raw_user_code)
                user_name = limpiar_string(row.get('Nombre de usuario') or row.get('nombre de usuario') or '')
                
                if not user_code or user_code == "-" or user_code == "Total" or user_code == "total":
                    continue
                    
                total_paginas = parse_int(row.get('Total páginas impresión', 0))
                total_bn = total_paginas
                total_color = 0
                
                copiadora_bn = 0
                copiadora_color = 0
                impresora_bn = total_paginas
                impresora_color = 0
                escaner_bn = 0
                escaner_color = 0
                fax_bn = 0
            else:
                raw_user_code = row.get('Usuario') or row.get('\\ufeffUsuario') or row.get('usuario')
                if not raw_user_code:
                    continue
                    
                user_code = limpiar_string(raw_user_code)
                user_name = limpiar_string(row.get('Nombre') or row.get('nombre') or '')
                
                if not user_code or user_code == "Total" or user_code == "total":
                    continue
                    
                total_paginas = parse_int(row.get('Total impresiones', 0))
                total_bn = parse_int(row.get('ByN(Total impresiones)', 0))
                total_color = parse_int(row.get('Color(Total impresiones)', 0))
                
                copiadora_bn = parse_int(row.get('Blanco y negroTotal(Copiadora/Document Server)', 0))
                copiadora_color = (
                    parse_int(row.get('Mono ColorTotal(Copiadora/Document Server)', 0)) +
                    parse_int(row.get('Dos coloresTotal(Copiadora/Document Server)', 0)) +
                    parse_int(row.get('A Todo ColorTotal(Copiadora/Document Server)', 0))
                )
                
                impresora_bn = parse_int(row.get('Blanco y negroTotal(Impresora)', 0))
                impresora_color = (
                    parse_int(row.get('Mono ColorTotal(Impresora)', 0)) +
                    parse_int(row.get('Dos coloresTotal(Impresora)', 0)) +
                    parse_int(row.get('ColorTotal(Impresora)', 0))
                )
                
                escaner_bn = parse_int(row.get('Blanco y negroTotal(Escáner)', 0))
                escaner_color = parse_int(row.get('A Todo ColorTotal(Escáner)', 0))
                
                fax_bn = parse_int(row.get('Blanco y negroTotal(Fax)', 0))

            # Buscar al usuario por código
            user = db.query(User).filter(User.codigo_de_usuario == user_code).first()
            if not user:
                print(f"   👤 User code '{user_code}' ({user_name}) not found. Creating user...")
                user = User(
                    username=f"user_{user_code}",
                    name=user_name,
                    codigo_de_usuario=user_code,
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Calcular consumos (diferencia)
            consumo_total = 0
            consumo_copiadora = 0
            consumo_impresora = 0
            consumo_escaner = 0
            consumo_fax = 0
            
            if user.id in lecturas_anteriores:
                prev = lecturas_anteriores[user.id]
                consumo_total = max(0, total_paginas - prev["total_paginas"])
                
                prev_copiadora = prev["copiadora_bn"] + prev["copiadora_color"]
                curr_copiadora = copiadora_bn + copiadora_color
                consumo_copiadora = max(0, curr_copiadora - prev_copiadora)
                
                prev_impresora = prev["impresora_bn"] + prev["impresora_color"]
                curr_impresora = impresora_bn + impresora_color
                consumo_impresora = max(0, curr_impresora - prev_impresora)
                
                prev_escaner = prev["escaner_bn"] + prev["escaner_color"]
                curr_escaner = escaner_bn + escaner_color
                consumo_escaner = max(0, curr_escaner - prev_escaner)
                
                consumo_fax = max(0, fax_bn - prev["fax_bn"])

            u_record = CierreMensualUsuario(
                user_id=user.id,
                total_paginas=total_paginas,
                total_bn=total_bn,
                total_color=total_color,
                copiadora_bn=copiadora_bn,
                copiadora_color=copiadora_color,
                impresora_bn=impresora_bn,
                impresora_color=impresora_color,
                escaner_bn=escaner_bn,
                escaner_color=escaner_color,
                fax_bn=fax_bn,
                consumo_total=consumo_total,
                consumo_copiadora=consumo_copiadora,
                consumo_impresora=consumo_impresora,
                consumo_escaner=consumo_escaner,
                consumo_fax=consumo_fax
            )
            usuarios_cierre.append(u_record)

    # 5. Calcular diferencias del totalizador físico de la impresora
    diferencia_total = 0
    diferencia_copiadora = 0
    diferencia_impresora = 0
    diferencia_escaner = 0
    diferencia_fax = 0
    
    if ultimo_cierre:
        diferencia_total = max(0, total_paginas_impresora - ultimo_cierre.total_paginas)
        diferencia_copiadora = max(0, total_copiadora_impresora - ultimo_cierre.total_copiadora)
        diferencia_impresora = max(0, total_impresora_impresora - ultimo_cierre.total_impresora)
        diferencia_escaner = max(0, total_escaner_impresora - ultimo_cierre.total_escaner)
        diferencia_fax = max(0, total_fax_impresora - ultimo_cierre.total_fax)
    
    # 6. Crear registro de CierreMensual con contadores físicos reales de pantalla
    cierre_nuevo = CierreMensual(
        printer_id=printer.id,
        fecha_inicio=date(2026, 5, 21),
        fecha_fin=date(2026, 6, 19),
        anio=2026,
        mes=6,
        total_paginas=total_paginas_impresora,
        total_copiadora=total_copiadora_impresora,
        total_impresora=total_impresora_impresora,
        total_escaner=total_escaner_impresora,
        total_fax=total_fax_impresora,
        diferencia_total=diferencia_total,
        diferencia_copiadora=diferencia_copiadora,
        diferencia_impresora=diferencia_impresora,
        diferencia_escaner=diferencia_escaner,
        diferencia_fax=diferencia_fax,
        cerrado_por="Carga Manual CSV",
        notas="Cierre de junio importado con contadores generales físicos tomados de capturas de pantalla WIM/Pantalla"
    )
    
    db.add(cierre_nuevo)
    db.commit()
    db.refresh(cierre_nuevo)
    
    # 7. Asignar los usuarios al cierre
    for u_rec in usuarios_cierre:
        u_rec.cierre_mensual_id = cierre_nuevo.id
        db.add(u_rec)
        
    db.commit()
    print(f"   ✅ Done! Closure created with ID {cierre_nuevo.id} for June 19, 2026.")
    print(f"      Total Printer Pages: {total_paginas_impresora:,} (Diff: +{diferencia_total:,})")
    print(f"      Imported users: {len(usuarios_cierre)}")
    return True

# Ejecución principal
db = SessionLocal()
try:
    csv_mappings = [
        ("E174M210096 19.06.2026.csv", "E174M210096"),
        ("E174MA11130 19.06.2026.csv", "E174MA11130"),
        ("E176M460020 19.06.2026.csv", "E176M460020"),
        ("G986XA16285 19.06.2026.csv", "G986XA16285"),
        ("W533L900719 19.06.2026.csv", "W533L900719")
    ]
    
    for filename, serial in csv_mappings:
        filepath = f"/app/docs/{filename}"
        if os.path.exists(filepath):
            import_csv_for_printer(db, filepath, serial)
        else:
            print(f"❌ File {filepath} not found inside container!")
            
except Exception as e:
    db.rollback()
    print(f"❌ Transaction failed: {e}")
finally:
    db.close()

EOF
docker cp /home/odootic/ricoh-app/docs/. ricoh-backend:/app/docs/
docker cp /tmp/import_june_closures.py ricoh-backend:/app/import_june_closures.py
docker exec -t ricoh-backend python /app/import_june_closures.py
"""

stdin, stdout, stderr = client.exec_command(import_python_code)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

client.close()
