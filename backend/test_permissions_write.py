#!/usr/bin/env python3
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add app to path
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db.repository import UserRepository, PrinterRepository, AssignmentRepository
from services.ricoh_web_client import get_ricoh_web_client

def test():
    db = SessionLocal()
    try:
        # User 3 = JUAN LIZARAZO
        user = UserRepository.get_by_id(db, 3)
        if not user:
            print("ERROR: User 3 not found")
            return
            
        # Printer 4 = 192.168.91.251 (3ER PISO ELITE BOYACA REAL)
        printer = PrinterRepository.get_by_id(db, 4)
        if not printer:
            print("ERROR: Printer 4 not found")
            return
            
        assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
        if not assignment or not assignment.entry_index:
            print("ERROR: Assignment or entry_index not found")
            return
            
        print(f"Testing permissions for User {user.name} (PIN {user.codigo_de_usuario}) on Printer {printer.hostname} ({printer.ip_address})")
        print(f"Entry index: {assignment.entry_index}")
        
        client = get_ricoh_web_client()
        
        # 1. Read current permissions
        print("\n--- 1. CURRENT LIVE PERMISSIONS ---")
        curr = client._get_user_details(printer.ip_address, assignment.entry_index, admin_password=printer.admin_password)
        print(f"Current permissions on device: {curr.get('permisos') if curr else 'ERROR'}")
        
        # 2. Write new permissions (Enable Copier, Printer, Scanner, disable others)
        print("\n--- 2. WRITING PERMISSIONS (Enable Copier, Printer, Scanner) ---")
        new_perms = {
            'copiadora': True,
            'copiadora_color': False,
            'impresora': False,
            'impresora_color': False,
            'escaner': False,
            'document_server': False,
            'fax': False,
            'navegador': False
        }
        success = client.set_user_functions(
            printer.ip_address,
            assignment.entry_index,
            new_perms,
            admin_password=printer.admin_password,
            set_password=False
        )
        print(f"Write success: {success}")
        
        # 3. Read back permissions
        print("\n--- 3. READ-BACK LIVE PERMISSIONS ---")
        after = client._get_user_details(printer.ip_address, assignment.entry_index, admin_password=printer.admin_password)
        print(f"Read-back permissions on device: {after.get('permisos') if after else 'ERROR'}")
        
        # Verify
        if after and after.get('permisos'):
            p = after['permisos']
            expected = {
                'copiadora': True,
                'impresora': False,
                'escaner': False,
                'document_server': False,
                'fax': False,
                'navegador': False
            }
            # Check matching keys
            all_match = True
            for k, val in expected.items():
                if p.get(k) != val:
                    print(f"❌ MISMATCH: {k} is {p.get(k)}, expected {val}")
                    all_match = False
            if all_match:
                print("✅ SUCCESS: Written permissions match read-back permissions perfectly!")
            else:
                print("❌ FAIL: Written permissions do not match read-back permissions.")
        else:
            print("ERROR: Could not read back permissions.")
            
    finally:
        db.close()

if __name__ == '__main__':
    test()
