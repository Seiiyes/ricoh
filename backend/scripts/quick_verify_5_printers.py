"""
Script rápido para verificar las 5 impresoras - solo resumen
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import SessionLocal
from db.models import Printer
from services.ricoh_web_client import RicohWebClient
import logging

logging.basicConfig(level=logging.WARNING)  # Solo warnings y errors
logger = logging.getLogger(__name__)


def quick_verify():
    db = SessionLocal()
    
    try:
        printers = db.query(Printer).filter(Printer.status != 'offline').all()
        print(f"\n{'='*80}")
        print(f"VERIFICACIÓN RÁPIDA DE LAS {len(printers)} IMPRESORAS")
        print(f"{'='*80}\n")
        
        client = RicohWebClient(admin_user="admin", admin_password="")
        
        results = []
        total_users = 0
        total_with_smb = 0
        
        for i, printer in enumerate(printers, 1):
            print(f"[{i}/{len(printers)}] {printer.hostname} ({printer.ip_address})...", end=" ", flush=True)
            
            try:
                users = client.read_users_from_printer(printer.ip_address, fast_list=True)
                users_with_path = [u for u in users if u.get('carpeta', '').strip()]
                
                results.append({
                    'hostname': printer.hostname,
                    'ip': printer.ip_address,
                    'total': len(users),
                    'con_smb': len(users_with_path)
                })
                
                total_users += len(users)
                total_with_smb += len(users_with_path)
                
                print(f"✅ {len(users)} usuarios, {len(users_with_path)} con SMB")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                results.append({
                    'hostname': printer.hostname,
                    'ip': printer.ip_address,
                    'total': 0,
                    'con_smb': 0
                })
        
        print(f"\n{'='*80}")
        print(f"RESUMEN FINAL")
        print(f"{'='*80}\n")
        
        for r in results:
            pct = (r['con_smb'] * 100 // r['total']) if r['total'] > 0 else 0
            print(f"{r['hostname']} ({r['ip']})")
            print(f"  Total: {r['total']}, Con SMB: {r['con_smb']} ({pct}%)")
        
        print(f"\n{'='*80}")
        print(f"TOTALES")
        print(f"{'='*80}")
        print(f"Total usuarios: {total_users}")
        print(f"Con ruta SMB: {total_with_smb} ({total_with_smb*100//total_users if total_users > 0 else 0}%)")
        print(f"{'='*80}\n")
        
    finally:
        db.close()


if __name__ == "__main__":
    quick_verify()
