import paramiko
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = "192.168.91.131"
USERNAME = "odootic"
PASSWORD = "Zuly152325*"

python_code = """
import asyncio
import time
from db.database import SessionLocal
from db.models import User, Printer, UserPrinterAssignment
from services.provisioning import ProvisioningService

db = SessionLocal()
try:
    # 1. Buscar el usuario 7104
    user = db.query(User).filter(User.codigo_de_usuario == "7104").first()
    if not user:
        print("❌ Error: Usuario 7104 no encontrado en la base de datos.")
        sys.exit(1)
    
    print(f"👤 Usuario encontrado: {user.name} (ID={user.id}, Código={user.codigo_de_usuario})")
    
    # 2. Buscar las impresoras 192.168.91.250, .251, .252, .253
    target_ips = ["192.168.91.250", "192.168.91.251", "192.168.91.252", "192.168.91.253"]
    printers = db.query(Printer).filter(Printer.ip_address.in_(target_ips)).all()
    if not printers:
        print("❌ Error: No se encontraron las impresoras objetivo en la base de datos.")
        sys.exit(1)
        
    print(f"🖨️  Impresoras encontradas ({len(printers)}):")
    for p in printers:
        print(f"   - ID={p.id} | IP={p.ip_address} | Hostname={p.hostname}")
        
    printer_ids = [p.id for p in printers]
    
    # 3. Limpiar asignaciones previas en la base de datos para simular una creación limpia
    print("\\n🧹 Limpiando asignaciones previas del usuario 7104 en base de datos para la prueba...")
    db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == user.id).delete()
    db.commit()
    print("✅ Asignaciones previas eliminadas de la base de datos.")
    
    # 4. Ejecutar aprovisionamiento concurrente
    print(f"\\n🚀 Iniciando aprovisionamiento CONCURRENTE para {len(printer_ids)} impresoras...")
    start_time = time.time()
    
    # provision_user_to_printers es sincrónico y utiliza ThreadPoolExecutor internamente
    result = ProvisioningService.provision_user_to_printers(db, user.id, printer_ids)
    
    elapsed = time.time() - start_time
    print(f"\\n⏱️  Aprovisionamiento finalizado en {elapsed:.2f} segundos.")
    print(f"Resultado General: success={result.get('success')} | mensaje={result.get('message')}")
    
    # 5. Consultar asignaciones guardadas en la base de datos
    db.close()
    db = SessionLocal()
    assignments = db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == user.id).all()
    print("\\n📊 RESULTADOS GUARDADOS EN BASE DE DATOS (UserPrinterAssignment):")
    print("-" * 80)
    for a in assignments:
        print(f"   IP={a.printer.ip_address} | Slot (entry_index)={a.entry_index} | Activo={a.is_active}")
        print(f"   Permisos: Copiador={a.func_copier} | Escáner={a.func_scanner} | Impresora={a.func_printer} | Color={a.func_printer_color}")
        print("-" * 80)
        
except Exception as e:
    import traceback
    print("❌ Excepción durante la ejecución del test:")
    print(traceback.format_exc())
finally:
    db.close()
"""

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
    print(f"[OK] CONECTADO a {HOST} vía SSH")
    
    # Escribir código python temporal en el servidor
    sftp = client.open_sftp()
    with sftp.open('/home/odootic/ricoh-app/backend/test_provision_run.py', 'w') as f:
        f.write(python_code)
    sftp.close()
    print("[OK] Script de test subido al servidor")
    
    # Ejecutar el script dentro de docker
    print("\n--- EJECUTANDO PRUEBA DE APROVISIONAMIENTO EN EL CONTENEDOR DOCKER ---")
    stdin, stdout, stderr = client.exec_command(f"echo '{PASSWORD}' | sudo -S docker exec ricoh-backend python test_provision_run.py")
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    if out:
        print(out)
    if err:
        print("\n[STDERR / SUDO PROMPT]:")
        print(err)
        
    # Limpiar script remoto
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_provision_run.py")
    print("\n[OK] Script temporal eliminado del servidor.")
    
except Exception as e:
    print(f"[ERROR]: {e}", file=sys.stderr)
finally:
    client.close()
