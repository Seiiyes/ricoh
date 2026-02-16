"""
Prueba de aprovisionamiento a múltiples impresoras
Simula el flujo completo: crear usuario y provisionarlo a varias impresoras
"""
import sys
import codecs
import random

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from services.ricoh_web_client import RicohWebClient

# Generar código aleatorio
random_code = random.randint(1000, 9999)

# Lista de impresoras de prueba (ajusta según tu red)
printer_ips = [
    "192.168.91.250",
    # "192.168.91.251",  # Descomenta si tienes más impresoras
    # "192.168.91.252",
]

# Datos de prueba
test_user = {
    "nombre": f"USUARIO MULTI {random_code}",
    "codigo_de_usuario": str(random_code),
    "nombre_usuario_inicio_sesion": "reliteltda\\scaner",
    "contrasena_inicio_sesion": "",  # Contraseña vacía
    "funciones_disponibles": {
        "copiadora": False,
        "impresora": False,
        "document_server": False,
        "fax": False,
        "escaner": True,  # Solo escáner habilitado
        "navegador": False
    },
    "carpeta_smb": {
        "protocolo": "SMB",
        "servidor": "TIC0596",
        "puerto": 21,
        "ruta": "\\\\TIC0596\\Escaner"
    }
}

print("\n" + "="*70)
print("🧪 PRUEBA DE APROVISIONAMIENTO A MÚLTIPLES IMPRESORAS")
print("="*70 + "\n")

print(f"📤 Usuario a provisionar:")
print(f"   Nombre: {test_user['nombre']}")
print(f"   Código: {test_user['codigo_de_usuario']}")
print(f"   Usuario de red: {test_user['nombre_usuario_inicio_sesion']}")
print(f"   Funciones: Escáner")
print(f"\n🖨️  Impresoras objetivo: {len(printer_ips)}")
for i, ip in enumerate(printer_ips, 1):
    print(f"   {i}. {ip}")

print("\n" + "-"*70 + "\n")

# Crear cliente
client = RicohWebClient(timeout=30, admin_user="admin", admin_password="")

# Provisionar a cada impresora
results = []
for i, printer_ip in enumerate(printer_ips, 1):
    print(f"\n📡 [{i}/{len(printer_ips)}] Provisionando a {printer_ip}...")
    
    try:
        success = client.provision_user(printer_ip, test_user)
        results.append({
            "ip": printer_ip,
            "success": success
        })
        
        if success:
            print(f"   ✅ Éxito en {printer_ip}")
        else:
            print(f"   ❌ Fallo en {printer_ip}")
    except Exception as e:
        print(f"   ❌ Error en {printer_ip}: {e}")
        results.append({
            "ip": printer_ip,
            "success": False,
            "error": str(e)
        })

# Resumen
print("\n" + "="*70)
print("📊 RESUMEN DE RESULTADOS")
print("="*70 + "\n")

successful = sum(1 for r in results if r["success"])
failed = len(results) - successful

print(f"✅ Exitosos: {successful}/{len(results)}")
print(f"❌ Fallidos: {failed}/{len(results)}")

if successful > 0:
    print(f"\n💡 Usuario '{test_user['nombre']}' (código: {test_user['codigo_de_usuario']}) ")
    print(f"   provisionado exitosamente en {successful} impresora(s)")
    print("\n🔍 Verifica en las impresoras:")
    for result in results:
        if result["success"]:
            print(f"   • http://{result['ip']}/web/entry/es/address/adrsList.cgi")

print("\n" + "="*70 + "\n")
