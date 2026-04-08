"""
Script para verificar el estado de las rutas SMB en la base de datos
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_smb_paths():
    """Verifica el estado de las rutas SMB"""
    db = SessionLocal()
    
    try:
        # Obtener todos los usuarios activos
        users = db.query(User).filter(User.is_active == True).all()
        
        total = len(users)
        con_ruta_especifica = 0
        con_ruta_generica = 0
        sin_ruta = 0
        
        rutas_especificas = []
        rutas_genericas = []
        
        for user in users:
            smb_path = user.smb_path or ''
            
            # Rutas genéricas/placeholder
            if smb_path in ['\\\\PENDIENTE\\Escaner', '\\\\192.168.91.5\\Escaner', '']:
                con_ruta_generica += 1
                rutas_genericas.append(f"{user.codigo_de_usuario} - {user.name}: {smb_path}")
            # Rutas específicas (de impresoras)
            elif any(x in smb_path for x in ['\\\\CFP-', '\\\\CF-', '\\\\TIC', '\\\\RECEPCION', '\\\\OPERACIONES']):
                con_ruta_especifica += 1
                if len(rutas_especificas) < 10:
                    rutas_especificas.append(f"{user.codigo_de_usuario} - {user.name}: {smb_path}")
            # Sin ruta
            elif not smb_path:
                sin_ruta += 1
            else:
                # Otras rutas (contar como específicas)
                con_ruta_especifica += 1
                if len(rutas_especificas) < 10:
                    rutas_especificas.append(f"{user.codigo_de_usuario} - {user.name}: {smb_path}")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"ESTADO DE RUTAS SMB")
        logger.info(f"{'='*80}")
        logger.info(f"Total de usuarios activos: {total}")
        logger.info(f"Con ruta específica: {con_ruta_especifica} ({con_ruta_especifica*100//total if total > 0 else 0}%)")
        logger.info(f"Con ruta genérica/placeholder: {con_ruta_generica} ({con_ruta_generica*100//total if total > 0 else 0}%)")
        logger.info(f"Sin ruta: {sin_ruta}")
        
        if rutas_especificas:
            logger.info(f"\n{'='*80}")
            logger.info(f"EJEMPLOS DE RUTAS ESPECÍFICAS (primeros 10):")
            logger.info(f"{'='*80}")
            for ruta in rutas_especificas:
                logger.info(f"  {ruta}")
        
        if rutas_genericas:
            logger.info(f"\n{'='*80}")
            logger.info(f"USUARIOS CON RUTAS GENÉRICAS (primeros 20):")
            logger.info(f"{'='*80}")
            for ruta in rutas_genericas[:20]:
                logger.info(f"  {ruta}")
        
    finally:
        db.close()


if __name__ == "__main__":
    check_smb_paths()
