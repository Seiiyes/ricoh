with open('backend/api/discovery.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The file might have changed. Let's find 'try:' starting get_user_details_endpoint
start_idx = -1
for i, line in enumerate(lines):
    if 'async def get_user_details_endpoint' in line:
        # The next 'try:' is our target
        for j in range(i+1, len(lines)):
            if 'try:' in lines[j]:
                start_idx = j
                break
        break

if start_idx == -1:
    print("Error: Could not find start of try block in get_user_details_endpoint")
    import sys
    sys.exit(1)

print(f"Found try block start at line {start_idx + 1}")

header = lines[:start_idx + 1]

insert_code = """        # Resolve printer password
        printer = PrinterRepository.get_by_ip(db, printer_ip)
        printer_pwd = printer.admin_password if printer else None

        ricoh_client = get_ricoh_web_client()
        # No reseteamos sesión aquí para aprovechar cookies si ya existen
        details = ricoh_client._get_user_details(printer_ip, entry_index, fast_sync=False, admin_password=printer_pwd)
        
        if not details:
            raise HTTPException(status_code=404, detail="No se pudieron obtener los detalles del usuario")
            
        return {
            "success": True,
            "ip": printer_ip,
            "entry_index": entry_index,
            "permisos": details.get('permisos', {}),
            "carpeta": details.get('carpeta', '')
        }
    except Exception as e:
        logger.error(f"Error obteniendo detalles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def scan_single_printer(
    printer_id: int,
    printer_hostname: str,
    printer_ip: str,
    printer_pwd: Optional[str],
    mode: str,
    user_code: Optional[str],
    ricoh_client
) -> dict:
    try:
        # IMPORTANTE: Resetear sesión ANTES de cada impresora para evitar conflictos de cookies
        ricoh_client.reset_session()
        logger.info(f"🔄 Sesión reseteada para impresora {printer_hostname} ({printer_ip})")
        
        if mode == "specific" and user_code is not None:
            # Buscar usuario específico (Incluye detalles/permisos automáticamente)
            logger.info(f"🎯 Llamando a find_specific_user para {printer_ip}, usuario {user_code}")
            user_found = ricoh_client.find_specific_user(printer_ip, user_code, admin_password=printer_pwd)
            logger.info(f"📋 Resultado de find_specific_user: {user_found}")
            if user_found:
                printer_users = [user_found]
            else:
                printer_users = []
        else:
            # Leer todos los usuarios de la impresora (MODO RÁPIDO - sin permisos)
            logger.info(f"📋 Leyendo lista de usuarios de {printer_ip}...")
            printer_users = ricoh_client.read_users_from_printer(printer_ip, fast_list=True, admin_password=printer_pwd)
            
        return {
            'printer_id': printer_id,
            'printer_hostname': printer_hostname,
            'printer_ip': printer_ip,
            'users': printer_users,
            'error': None
        }
    except Exception as e:
        logger.error(f"Error en {printer_hostname} ({printer_ip}) durante escaneo concurrente: {e}")
        return {
            'printer_id': printer_id,
            'printer_hostname': printer_hostname,
            'printer_ip': printer_ip,
            'users': [],
            'error': str(e)
        }


@router.post("/sync-users-from-printers", status_code=status.HTTP_200_OK)
async def sync_users_from_printers(
    user_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    \"\"\"
    Lee usuarios desde todas las impresoras físicas y los agrupa por código de usuario
    
    Args:
        user_code: Código de usuario específico a buscar (opcional). Si se proporciona,
                   solo busca ese usuario en todas las impresoras.
    
    Returns:
        Lista de usuarios únicos con información de en qué impresoras están registrados
    \"\"\"
    from services.ricoh_web_client import get_ricoh_web_client
    from services.ricoh_selenium_client import close_selenium_client
    from db.repository import UserRepository
    
    logger.info("=" * 70)
"""

# Find the next place containing "logger.info("=" * 70)" to connect the footer
footer_idx = -1
for i in range(start_idx + 1, len(lines)):
    if 'INICIANDO SINCRONIZACIÓN' in lines[i]:
        # The line containing INICIANDO is after the logger.info("=" * 70)
        # Let's verify and get the line after it
        footer_idx = i + 2
        break

if footer_idx == -1:
    print("Error: Could not find footer match")
    import sys
    sys.exit(1)

print(f"Found footer start at line {footer_idx + 1}")

footer = lines[footer_idx:]

new_content = ''.join(header) + insert_code + ''.join(footer)

with open('backend/api/discovery.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ File modified successfully!")
