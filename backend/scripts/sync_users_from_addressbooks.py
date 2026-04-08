"""
Script para sincronizar usuarios desde libretas de direcciones de todas las impresoras.
Actualiza las rutas SMB reales de los usuarios.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer, User
from services.ricoh_web_client import RicohWebClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_users_from_all_printers():
    """Sincroniza usuarios desde libretas de direcciones de todas las impresoras activas"""
    db = SessionLocal()
    
    try:
        # Obtener impresoras activas
        printers = db.query(Printer).filter(Printer.status != 'offline').all()
        logger.info(f"Encontradas {len(printers)} impresoras activas")
        
        client = RicohWebClient(admin_user="admin", admin_password="")
        
        total_created = 0
        total_updated = 0
        total_existing = 0
        
        for printer in printers:
            logger.info(f"\n{'='*80}")
            logger.info(f"Procesando impresora: {printer.hostname} ({printer.ip_address})")
            logger.info(f"{'='*80}")
            
            try:
                # Leer usuarios desde la impresora (modo rápido para obtener carpetas)
                users_from_printer = client.read_users_from_printer(printer.ip_address, fast_list=True)
                
                if not users_from_printer:
                    logger.warning(f"No se pudieron leer usuarios de {printer.hostname}")
                    continue
                
                logger.info(f"Encontrados {len(users_from_printer)} usuarios en libreta")
                
                for user_data in users_from_printer:
                    codigo = user_data.get('codigo', '').strip()
                    nombre = user_data.get('nombre', '').strip()
                    carpeta = user_data.get('carpeta', '').strip()
                    
                    if not codigo or not nombre:
                        continue
                    
                    # Buscar usuario en BD
                    user = db.query(User).filter(User.codigo_de_usuario == codigo).first()
                    
                    if user:
                        # Usuario existe - actualizar ruta SMB si tiene carpeta y es diferente
                        if carpeta and carpeta != user.smb_path:
                            # Solo actualizar si la ruta actual es placeholder o genérica
                            if user.smb_path in ['\\\\PENDIENTE\\Escaner', '\\\\192.168.91.5\\Escaner', '']:
                                old_path = user.smb_path
                                user.smb_path = carpeta
                                total_updated += 1
                                logger.info(f"  ✓ Actualizado {codigo} - {nombre}: {old_path} → {carpeta}")
                            else:
                                total_existing += 1
                        else:
                            total_existing += 1
                    else:
                        # Usuario no existe - crear con ruta SMB
                        new_user = User(
                            name=nombre,
                            codigo_de_usuario=codigo,
                            network_username="reliteltda\\scaner",
                            network_password_encrypted="",
                            smb_server="192.168.91.5",
                            smb_port=21,
                            smb_path=carpeta if carpeta else "\\\\192.168.91.5\\Escaner",
                            func_copier=False,
                            func_printer=False,
                            func_scanner=False,
                            is_active=True
                        )
                        db.add(new_user)
                        total_created += 1
                        logger.info(f"  ✓ Creado {codigo} - {nombre} (SMB: {new_user.smb_path})")
                
                # Commit después de cada impresora
                db.commit()
                logger.info(f"✓ Impresora {printer.hostname} completada")
                
            except Exception as e:
                logger.error(f"Error procesando impresora {printer.hostname}: {e}")
                db.rollback()
                continue
        
        logger.info(f"\n{'='*80}")
        logger.info(f"RESUMEN FINAL:")
        logger.info(f"  Usuarios creados: {total_created}")
        logger.info(f"  Usuarios actualizados: {total_updated}")
        logger.info(f"  Usuarios sin cambios: {total_existing}")
        logger.info(f"{'='*80}")
        
    finally:
        db.close()


if __name__ == "__main__":
    sync_users_from_all_printers()
