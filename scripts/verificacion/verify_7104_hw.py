"""
Script to verify and restore real permissions for user 7104 from physical printers.
Reads each printer and checks what permissions user 7104 actually has there.
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

from db.database import SessionLocal
from db import models
from db.repository import UserRepository, PrinterRepository, AssignmentRepository
from services.ricoh_web_client import get_ricoh_web_client

db = SessionLocal()
try:
    # Get user 7104
    user = db.query(models.User).filter(models.User.codigo_de_usuario == '7104').first()
    if not user:
        print("User 7104 NOT FOUND")
        sys.exit(1)
    
    print(f"User 7104: ID={user.id}, name={user.name}")
    
    # Get all printers
    printers = db.query(models.Printer).all()
    print(f"\nChecking {len(printers)} printers...")
    
    client = get_ricoh_web_client()
    
    for printer in printers:
        print(f"\n{'='*60}")
        print(f"Printer: {printer.hostname} @ {printer.ip_address}")
        
        # Check DB assignment
        assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
        if assignment:
            print(f"  DB Assignment: ID={assignment.id}, entry_index={assignment.entry_index}")
            print(f"  DB Permissions: copier={assignment.func_copier}, printer={assignment.func_printer}, scanner={assignment.func_scanner}")
        else:
            print(f"  DB Assignment: NONE")
        
        # Read from physical printer
        print(f"  Reading from physical printer...")
        try:
            user_in_printer = client.find_specific_user(
                printer.ip_address, 
                user.codigo_de_usuario,
                admin_password=printer.admin_password
            )
            if user_in_printer:
                entry_index = user_in_printer.get('entry_index')
                permisos = user_in_printer.get('permisos', {})
                print(f"  PRINTER: Found! entry_index={entry_index}")
                print(f"  PRINTER Permissions: {permisos}")
                
                # If DB has wrong permissions, offer to fix
                if assignment and permisos:
                    db_copier = assignment.func_copier
                    hw_copier = permisos.get('copiadora', False)
                    if db_copier != hw_copier:
                        print(f"  ⚠️  MISMATCH! DB says copier={db_copier} but printer says {hw_copier}")
                        print(f"  🔧 Updating DB to match printer...")
                        AssignmentRepository.update_assignment_state(
                            db, user.id, printer.id,
                            permissions={
                                'copiadora': permisos.get('copiadora', False),
                                'copiadora_color': permisos.get('copiadora_color', False),
                                'impresora': permisos.get('impresora', False),
                                'impresora_color': permisos.get('impresora_color', False),
                                'escaner': permisos.get('escaner', False),
                                'document_server': permisos.get('document_server', False),
                                'fax': permisos.get('fax', False),
                                'navegador': permisos.get('navegador', False),
                            },
                            entry_index=entry_index
                        )
                        print(f"  ✅ DB updated!")
                elif assignment and not assignment.entry_index and entry_index:
                    print(f"  🔧 Updating entry_index in DB (was None)...")
                    assignment.entry_index = entry_index
                    db.commit()
                    print(f"  ✅ entry_index updated to {entry_index}")
            else:
                print(f"  PRINTER: User NOT FOUND")
        except Exception as e:
            print(f"  ERROR reading printer: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("=== FINAL STATE IN DB ===")
    assignments = db.query(models.UserPrinterAssignment).filter(
        models.UserPrinterAssignment.user_id == user.id
    ).all()
    for a in assignments:
        printer = db.query(models.Printer).filter(models.Printer.id == a.printer_id).first()
        print(f"\n  Printer {printer.ip_address} ({printer.hostname}):")
        print(f"    entry_index={a.entry_index}, is_active={a.is_active}")
        print(f"    copier={a.func_copier}, printer={a.func_printer}, scanner={a.func_scanner}")

finally:
    db.close()
