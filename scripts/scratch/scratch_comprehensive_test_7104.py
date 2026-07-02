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
import sys
from db.database import SessionLocal
from db.models import User, Printer, UserPrinterAssignment
from services.provisioning import ProvisioningService
from services.ricoh_web_client import get_ricoh_web_client

def print_separator(title):
    print("\\n" + "=" * 80)
    print(f"🔹 {title}")
    print("=" * 80)

db = SessionLocal()
try:
    # STEP 1: Buscar el usuario 7104 y establecer permisos específicos
    print_separator("PASO 1: Configurar permisos iniciales para el usuario 7104 en base de datos")
    user = db.query(User).filter(User.codigo_de_usuario == "7104").first()
    if not user:
        print("❌ Error: Usuario 7104 no encontrado en la base de datos.")
        sys.exit(1)
        
    print(f"👤 Usuario encontrado: {user.name} (ID={user.id}, Código={user.codigo_de_usuario})")
    
    # Activar permisos específicos: copiadora y escáner
    user.func_copier = True
    user.func_scanner = True
    user.func_printer = False
    user.func_printer_color = False
    user.func_copier_color = False
    db.commit()
    print("✅ Permisos actualizados en la tabla User: Copiadora=True | Escáner=True | Impresora=False")

    # STEP 2: Obtener las impresoras activas
    print_separator("PASO 2: Obtener impresoras activas para el aprovisionamiento")
    target_ips = ["192.168.91.250", "192.168.91.251", "192.168.91.252", "192.168.91.253"]
    printers = db.query(Printer).filter(Printer.ip_address.in_(target_ips)).all()
    if not printers:
        print("❌ Error: No se encontraron las impresoras objetivo en la base de datos.")
        sys.exit(1)
        
    print(f"🖨️ Impresoras encontradas ({len(printers)}):")
    for p in printers:
        print(f"   - ID={p.id} | IP={p.ip_address} | Hostname={p.hostname}")
    printer_ids = [p.id for p in printers]

    # STEP 3: Limpiar asignaciones previas para hacer un test limpio
    print_separator("PASO 3: Limpiar asignaciones previas en la base de datos")
    db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == user.id).delete()
    db.commit()
    print("✅ Asignaciones previas eliminadas de la base de datos.")

    # STEP 4: Ejecutar aprovisionamiento concurrente con nuevos permisos
    print_separator("PASO 4: Ejecutar Aprovisionamiento Concurrente (Simula botón Acciones -> Aprovisionar)")
    start_time = time.time()
    result = ProvisioningService.provision_user_to_printers(db, user.id, printer_ids)
    elapsed = time.time() - start_time
    print(f"⏱️ Aprovisionamiento finalizado en {elapsed:.2f} segundos.")
    print(f"Resultado General: success={result.get('success')} | mensaje={result.get('message')}")

    # Refrescar sesión para leer cambios guardados
    db.close()
    db = SessionLocal()
    
    # STEP 5: Verificar asignaciones guardadas y permisos reflejados en DB
    print_separator("PASO 5: Verificar asignaciones y permisos en la base de datos (UserPrinterAssignment)")
    assignments = db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == user.id).all()
    for a in assignments:
        print(f"🖨️ IP={a.printer.ip_address} | Slot={a.entry_index} | Activo={a.is_active}")
        print(f"   Permisos en DB: Copiadora={a.func_copier} | Escáner={a.func_scanner} | Impresora={a.func_printer}")
        if not (a.func_copier == True and a.func_scanner == True and a.func_printer == False):
            print("❌ ERROR: Los permisos de asignación en DB no coinciden con los del usuario.")
        else:
            print("✅ Permisos en DB correctos.")

    # STEP 6: Consultar el hardware de una de las impresoras para validar que los permisos se escribieron físicamente
    print_separator("PASO 6: Consultar el hardware de la impresora para verificar permisos reales")
    test_assignment = assignments[0]
    printer_ip = test_assignment.printer.ip_address
    entry_index = test_assignment.entry_index
    print(f"Leyendo detalles en la impresora {printer_ip} en el slot {entry_index}...")
    
    ricoh_client = get_ricoh_web_client()
    ricoh_client.reset_session()
    details = ricoh_client._get_user_details(printer_ip, entry_index, fast_sync=False, admin_password=test_assignment.printer.admin_password)
    
    if details:
        print(f"📂 Detalles leídos físicamente de la impresora {printer_ip}:")
        print(f"   Nombre: {details.get('nombre')}")
        print(f"   Código: {details.get('codigo_de_usuario')}")
        print(f"   Carpeta: {details.get('carpeta')}")
        perm = details.get('permisos', {})
        print(f"   Permisos Físicos: Copiadora={perm.get('copiadora')} | Escáner={perm.get('escaner')} | Impresora={perm.get('impresora')}")
        
        # Validar permisos leídos
        if perm.get('copiadora') == True and perm.get('escaner') == True and perm.get('impresora') == False:
            print("✅ CONFIRMADO: Los permisos físicos en la impresora coinciden perfectamente!")
        else:
            print("❌ ERROR: Los permisos físicos en la impresora NO coinciden.")
    else:
        print("❌ Error: No se pudieron leer los detalles de la impresora.")

    # STEP 7: Modificar los permisos para una impresora específica (Acción Editar permisos por equipo)
    print_separator("PASO 7: Modificar permisos para una impresora específica (Acción de Modificación)")
    target_printer = test_assignment.printer
    print(f"Cambiando permisos del usuario {user.name} en {target_printer.ip_address}: Habilitar Impresora=True")
    
    new_permissions = {
        'copiadora': True,
        'copiadora_color': False,
        'impresora': True,
        'impresora_color': False,
        'escaner': True,
        'document_server': False,
        'fax': False,
        'navegador': False
    }
    
    # 7.1. Actualizar en hardware
    ricoh_client.reset_session()
    hw_success = ricoh_client.set_user_functions(target_printer.ip_address, entry_index, new_permissions, admin_password=target_printer.admin_password)
    print(f"   Sincronización con hardware: {'✅ EXITOSO' if hw_success else '❌ FALLIDO'}")
    
    # 7.2. Actualizar en la base de datos
    from db.repository import AssignmentRepository
    db_success = AssignmentRepository.update_assignment_state(db, user.id, target_printer.id, permissions=new_permissions)
    print(f"   Actualización en base de datos: {'✅ EXITOSO' if db_success else '❌ FALLIDO'}")
    
    # 7.3. Volver a leer del hardware para verificar la modificación
    ricoh_client.reset_session()
    updated_details = ricoh_client._get_user_details(target_printer.ip_address, entry_index, fast_sync=False, admin_password=target_printer.admin_password)
    if updated_details:
        perm = updated_details.get('permisos', {})
        print(f"   Permisos Físicos Actualizados: Copiadora={perm.get('copiadora')} | Escáner={perm.get('escaner')} | Impresora={perm.get('impresora')}")
        if perm.get('impresora') == True:
            print("✅ CONFIRMADO: La modificación de permisos se reflejó correctamente en la impresora física!")
        else:
            print("❌ ERROR: La modificación de permisos no se reflejó en la impresora.")

    # STEP 8: Eliminar asignaciones (Simula botón Acciones -> Eliminar/Desasignar)
    print_separator("PASO 8: Eliminar asignaciones del usuario (Simula Acción Eliminar)")
    print(f"Eliminando asignaciones del usuario en las impresoras: {printer_ids}")
    remove_result = ProvisioningService.remove_user_from_printers(db, user.id, printer_ids)
    print(f"Resultado de eliminación: {remove_result}")
    
    # Refrescar y validar que no queden asignaciones activas
    db.close()
    db = SessionLocal()
    remaining_assignments = db.query(UserPrinterAssignment).filter(
        UserPrinterAssignment.user_id == user.id,
        UserPrinterAssignment.is_active == True
    ).all()
    print(f"Asignaciones activas restantes en DB: {len(remaining_assignments)}")
    if len(remaining_assignments) == 0:
        print("✅ CONFIRMADO: Todas las asignaciones se desactivaron correctamente en el sistema.")
    else:
        print("❌ ERROR: Aún quedan asignaciones activas en DB.")

    # Restaurar al usuario a un estado inicial activo y limpio para que quede bien registrado
    print_separator("RESTAURACIÓN: Volver a aprovisionar al usuario para dejarlo activo y limpio")
    user = db.query(User).filter(User.codigo_de_usuario == "7104").first()
    user.func_copier = True
    user.func_scanner = True
    user.func_printer = True
    user.func_printer_color = False
    db.commit()
    ProvisioningService.provision_user_to_printers(db, user.id, printer_ids)
    print("✅ Usuario 7104 restaurado con permisos estándar en las 4 impresoras.")

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
    with sftp.open('/home/odootic/ricoh-app/backend/test_comprehensive_actions.py', 'w') as f:
        f.write(python_code)
    sftp.close()
    print("[OK] Script de test subido al servidor")
    
    # Ejecutar el script dentro de docker
    print("\n--- EJECUTANDO PRUEBAS COMPLEMENTARIAS EN EL CONTENEDOR DOCKER ---")
    stdin, stdout, stderr = client.exec_command(f"echo '{PASSWORD}' | sudo -S docker exec ricoh-backend python test_comprehensive_actions.py")
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    if out:
        print(out)
    if err:
        print("\n[STDERR / SUDO PROMPT]:")
        print(err)
        
    # Limpiar script remoto
    client.exec_command("rm /home/odootic/ricoh-app/backend/test_comprehensive_actions.py")
    print("\n[OK] Script temporal eliminado del servidor.")
    
except Exception as e:
    print(f"[ERROR]: {e}", file=sys.stderr)
finally:
    client.close()
