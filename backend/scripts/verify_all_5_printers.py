"""
Script para verificar que se leyeron correctamente las 5 impresoras
y mostrar estadísticas detalladas de cada una
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer
from services.ricoh_web_client import RicohWebClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_all_5_printers():
    """Verifica que se lean correctamente las 5 impresoras"""
    db = SessionLocal()
    
    try:
        # Obtener todas las impresoras
        printers = db.query(Printer).filter(Printer.status != 'offline').all()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"VERIFICACIÓN DE LAS 5 IMPRESORAS")
        logger.info(f"{'='*80}")
        logger.info(f"Total de impresoras activas en BD: {len(printers)}\n")
        
        if len(printers) != 5:
            logger.warning(f"⚠️  ADVERTENCIA: Se esperaban 5 impresoras, pero hay {len(printers)}")
        
        client = RicohWebClient(admin_user="admin", admin_password="")
        
        all_users_by_printer = {}
        total_users_all_printers = 0
        total_with_smb_path = 0
        
        for i, printer in enumerate(printers, 1):
            logger.info(f"{'='*80}")
            logger.info(f"[{i}/{len(printers)}] {printer.hostname}")
            logger.info(f"{'='*80}")
            logger.info(f"IP: {printer.ip_address}")
            
            try:
                # Leer usuarios (modo rápido)
                logger.info(f"\nLeyendo usuarios...")
                users = client.read_users_from_printer(printer.ip_address, fast_list=True)
                
                if not users:
                    logger.error(f"❌ No se pudieron leer usuarios")
                    continue
                
                logger.info(f"✅ Total usuarios leídos: {len(users)}")
                
                # Contar usuarios con ruta SMB
                users_with_path = [u for u in users if u.get('carpeta', '').strip()]
                logger.info(f"✅ Usuarios con ruta SMB: {len(users_with_path)}")
                
                # Mostrar ejemplos de rutas SMB
                if users_with_path:
                    logger.info(f"\nEjemplos de rutas SMB (primeros 5):")
                    for j, user in enumerate(users_with_path[:5], 1):
                        logger.info(f"  {j}. {user['codigo']} - {user['nombre']}: {user['carpeta']}")
                
                # Guardar para resumen
                all_users_by_printer[printer.hostname] = {
                    'total': len(users),
                    'con_ruta': len(users_with_path),
                    'ip': printer.ip_address
                }
                
                total_users_all_printers += len(users)
                total_with_smb_path += len(users_with_path)
                
            except Exception as e:
                logger.error(f"❌ Error leyendo impresora: {e}")
                import traceback
                logger.error(traceback.format_exc())
            
            logger.info("")
        
        # Resumen final
        logger.info(f"{'='*80}")
        logger.info(f"RESUMEN DE LAS {len(printers)} IMPRESORAS")
        logger.info(f"{'='*80}")
        
        for hostname, data in all_users_by_printer.items():
            logger.info(f"{hostname} ({data['ip']})")
            logger.info(f"  Total usuarios: {data['total']}")
            logger.info(f"  Con ruta SMB: {data['con_ruta']} ({data['con_ruta']*100//data['total'] if data['total'] > 0 else 0}%)")
            logger.info("")
        
        logger.info(f"{'='*80}")
        logger.info(f"TOTALES GENERALES")
        logger.info(f"{'='*80}")
        logger.info(f"Total de usuarios en todas las impresoras: {total_users_all_printers}")
        logger.info(f"Total con ruta SMB específica: {total_with_smb_path}")
        logger.info(f"Porcentaje con ruta SMB: {total_with_smb_path*100//total_users_all_printers if total_users_all_printers > 0 else 0}%")
        
        if len(printers) == 5 and total_with_smb_path > 0:
            logger.info(f"\n✅ ¡ÉXITO! Las 5 impresoras fueron escaneadas correctamente")
        else:
            logger.warning(f"\n⚠️  Verificar: {len(printers)} impresoras escaneadas")
        
    finally:
        db.close()


if __name__ == "__main__":
    verify_all_5_printers()
