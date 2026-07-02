import paramiko
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from ssh_config import load_ssh_config
HOST, USER, PASS = load_ssh_config()

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15, look_for_keys=False, allow_agent=False)

# Comando para ejecutar dentro del contenedor docker backend (sin emojis para evitar errores de codificación en terminal Windows)
cmd = """docker exec ricoh-backend python -c "
from db.database import SessionLocal
from db.models_auth import AdminSession, AdminUser
from datetime import datetime, timezone
from collections import Counter

db = SessionLocal()
now = datetime.now(timezone.utc)

total_sessions = db.query(AdminSession).count()
active_sessions = db.query(AdminSession).filter(AdminSession.expires_at > now).all()
expired_sessions = db.query(AdminSession).filter(AdminSession.expires_at <= now).count()

print(f'STATS_TOTAL: {total_sessions}')
print(f'STATS_ACTIVE: {len(active_sessions)}')
print(f'STATS_EXPIRED: {expired_sessions}')

print('\\n=== DETALLE DE SESIONES ACTIVAS ===')
for s in active_sessions:
    user = db.query(AdminUser).filter(AdminUser.id == s.admin_user_id).first()
    username = user.username if user else 'Unknown'
    rol = user.rol if user else 'Unknown'
    time_left = s.expires_at - now
    hours_left = time_left.total_seconds() / 3600.0
    print(f'- Usuario: {username} ({rol}) | IP: {s.ip_address} | Expira en: {hours_left:.2f}h | Creado: {s.created_at.strftime(\\"%Y-%m-%d %H:%M:%S\\")}')

print('\\n=== SESIONES ACTIVAS POR IP ===')
ips = [s.ip_address for s in active_sessions]
for ip, count in Counter(ips).items():
    print(f'- IP {ip}: {count} sesion(es)')

print('\\n=== DETECCION DE ANOMALIAS ===')
user_ips = {}
for s in active_sessions:
    user = db.query(AdminUser).filter(AdminUser.id == s.admin_user_id).first()
    username = user.username if user else 'Unknown'
    if username not in user_ips:
        user_ips[username] = set()
    user_ips[username].add(s.ip_address)

anomalies = False
for username, ip_set in user_ips.items():
    if len(ip_set) > 1:
        print(f'[ALERTA] Usuario \\'{username}\\' tiene sesiones activas concurrentes desde multiples IPs: {list(ip_set)}')
        anomalies = True

if not anomalies:
    print('[OK] Ningun usuario posee sesiones concurrentes desde diferentes direcciones IP')

db.close()
"
"""

stdin, stdout, stderr = client.exec_command(cmd)
# Leer salida cruda de bytes y decodificar reemplazando errores
out_bytes = stdout.read()
print(out_bytes.decode('utf-8', errors='replace'))

err = stderr.read()
if err:
    print("=== ERROR ===")
    print(err.decode('utf-8', errors='replace'))

client.close()
