"""
Prueba final con índice aleatorio
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

# Generar índice aleatorio entre 100-999
random_index = random.randint(100, 999)
random_code = random.randint(1000, 9999)

# Datos de prueba
printer_ip = "192.168.91.250"
test_user = {
    "nombre": f"TEST USER {random_code}",
    "codigo_de_usuario": str(random_code),
    "nombre_usuario_inicio_sesion": "reliteltda\\scaner",  # Corregido el typo
    "contrasena_inicio_sesion": "",  # VACÍA
    "funciones_disponibles": {
        "copiadora": True,
        "impresora": True,
        "document_server": False,
        "fax": False,
        "escaner": True,
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
print("🧪 PRUEBA FINAL CON ÍNDICE AUTOINCREMENTAL")
print("="*70 + "\n")

# Crear cliente
client = RicohWebClient(timeout=30, admin_user="admin", admin_password="")

# Provisionar
print(f"📤 Provisionando usuario: {test_user['nombre']}")
print(f"   Código: {test_user['codigo_de_usuario']}")
print(f"   Índice: AUTOINCREMENTAL (asignado por la impresora)")
print(f"   Usuario de red: {test_user['nombre_usuario_inicio_sesion']}")
print(f"   Impresora: {printer_ip}\n")

# Modificar temporalmente el código para usar el índice aleatorio
import services.ricoh_web_client as rwc_module

# Guardar el método original
original_provision = rwc_module.RicohWebClient.provision_user

def provision_with_random_index(self, printer_ip, user_config):
    # Llamar al original pero interceptar para cambiar el índice
    return original_provision(self, printer_ip, user_config)

# No necesitamos modificar, el índice ya se genera en el código

success = client.provision_user(printer_ip, test_user)

print("\n" + "="*70)
if success:
    print("✅ PROVISIONAMIENTO EXITOSO")
    print("\n💡 Verifica en la impresora:")
    print(f"   1. Ve a: http://{printer_ip}/web/entry/es/address/adrsList.cgi")
    print(f"   2. Busca el usuario con código: {test_user['codigo_de_usuario']}")
    print(f"   3. Nombre: {test_user['nombre']}")
else:
    print("❌ PROVISIONAMIENTO FALLIDO")
    print("\n🔍 Revisa el archivo provision_response.html para ver el error")

print("="*70 + "\n")
