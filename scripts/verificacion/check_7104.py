import sys
sys.path.insert(0, '/app')

from db.database import SessionLocal
from db import models

db = SessionLocal()
try:
    # Get user 7104
    user = db.query(models.User).filter(models.User.codigo_de_usuario == '7104').first()
    if not user:
        print("User 7104 NOT FOUND in DB")
    else:
        print(f"User found: ID={user.id}, name={user.name}, active={user.is_active}")
        
        # Get all assignments
        assignments = db.query(models.UserPrinterAssignment).filter(
            models.UserPrinterAssignment.user_id == user.id
        ).all()
        print(f"\nAssignments ({len(assignments)} total):")
        for a in assignments:
            printer = db.query(models.Printer).filter(models.Printer.id == a.printer_id).first()
            printer_ip = printer.ip_address if printer else "?"
            printer_host = printer.hostname if printer else "Unknown"
            
            print(f"\n  Printer {a.printer_id} ({printer_host} @ {printer_ip}):")
            print(f"    is_active={a.is_active}, entry_index={a.entry_index}")
            print(f"    func_copier={a.func_copier}, func_printer={a.func_printer}, func_scanner={a.func_scanner}")
            print(f"    func_copier_color={a.func_copier_color}, func_printer_color={a.func_printer_color}")
            print(f"    func_document_server={a.func_document_server}, func_fax={a.func_fax}, func_browser={a.func_browser}")
finally:
    db.close()
