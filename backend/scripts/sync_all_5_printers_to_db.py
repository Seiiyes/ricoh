"""
Script para sincronizar las rutas SMB de las 5 impresoras a la base de datos
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


def sync_all_printers_to_db():
    """Sincroniza rutas SMB de las 5 impresoras a la BD"""
    db = SessionLocal()
    
    try:
        printers = db.query(Printer).filter(Printer.status != 'offline').all()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"SINCRONIZACIÓN DE {len(printers)} IMPRESORAS A BASE DE DATOS")
        logger.info(f"{'='*80}\n")
        
        client = RicohWebClient(admin_user="admin", admin_password="")
        
        # Diccionario: codigo_usuario -> ruta_smb
        smb_paths_by_code = {}
        
        for i, printer in enumerate(printers, 1):
            logger.info(f"[{i}/{len(printers)}] {printer.hostname} ({printer.ip_address})")
            
            try:
                users = client.read_users_from_printer(printer.ip_address, fast_list=True)
                
                logger.info(f"  Total usuarios: {len(users)}")
                
                count_with_smb = 0
                for user_data in users:
                    codigo = user_data.get('codigo', '').strip()
                    carpeta = user_data.get('carpeta', '').strip()
                    
                    if codigo and carpeta:
                        # Solo guardar si tiene ruta SMB específica (no vacía, no FTP)
                        if carpeta and '\\\\' in carpeta:
                            smb_paths_by_code[codigo] = carpeta
                            count_with_smb += 1
                
                logger.info(f"  Con ruta SMB: {count_with_smb}")
                
            except Exception as e:
                logger.error(f"  ❌ Error: {e}")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"ACTUALIZANDO BASE DE DATOS")
        logger.info(f"{'='*80}")
        logger.info(f"Total de rutas SMB únicas recolectadas: {len(smb_paths_by_code)}\n")
        
        # Actualizar usuarios en BD
        updated = 0
        not_found = 0
        
        for codigo, smb_path in smb_paths_by_code.items():
            user = db.query(User).filter(User.codigo_de_usuario == codigo).first()
            
            if user:
                # Solo actualizar si la ruta actual es genérica o diferente
                if user.smb_path in ['\\\\PENDIENTE\\Escaner', '\\\\192.168.91.5\\Escaner', ''] or user.smb_path != smb_path:
                    user.smb_path = smb_path
                    updated += 1
                    if updated <= 10:
                        logger.info(f"  ✓ {codigo} - {user.name}: {smb_path}")
            else:
                not_found += 1
        
        db.commit()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"RESUMEN DE SINCRONIZACIÓN")
        logger.info(f"{'='*80}")
        logger.info(f"Usuarios actualizados: {updated}")
        logger.info(f"Usuarios no encontrados en BD: {not_found}")
        
        # Verificación final
        logger.info(f"\n{'='*80}")
        logger.info(f"VERIFICACIÓN FINAL EN BASE DE DATOS")
        logger.info(f"{'='*80}")
        
        total_users = db.query(User).filter(User.is_active == True).count()
        
        users_with_specific = 0
        users_with_default = 0
        users_with_generic = 0
        
        for user in db.query(User).filter(User.is_active == True).all():
            smb_path = user.smb_path or ''
            
            if smb_path == '\\\\192.168.91.5\\Escaner':
                users_with_default += 1
            elif '\\\\\\\\192.168.91.5\\\\' in smb_path or smb_path == '\\\\PENDIENTE\\Escaner':
                users_with_generic += 1
            elif smb_path and any(x in smb_path for x in ['\\\\CFP-', '\\\\CF-', '\\\\TIC', '\\\\RECEPCION', '\\\\OPERACIONES', '\\\\DESKTOP-', '\\\\COMERCIAL', '\\\\ANALISTACONSUMO']):
                users_with_specific += 1
            elif smb_path:
                users_with_specific += 1
        
        logger.info(f"Total usuarios activos: {total_users}")
        logger.info(f"Con ruta específica de impresora: {users_with_specific} ({users_with_specific*100//total_users}%)")
        logger.info(f"Con ruta por defecto: {users_with_default} ({users_with_default*100//total_users}%)")
        logger.info(f"Con ruta genérica (error): {users_with_generic}")
        
        if users_with_generic == 0:
            logger.info(f"\n✅ ¡ÉXITO! Todos los usuarios tienen rutas SMB válidas")
        else:
            logger.warning(f"\n⚠️  Aún hay {users_with_generic} usuarios con rutas genéricas")
        
    finally:
        db.close()


if __name__ == "__main__":
    sync_all_printers_to_db()
