from db.database import SessionLocal
from db.models import User, UserPrinterAssignment
import sys

db = SessionLocal()
try:
    user = db.query(User).filter(User.codigo_de_usuario == '7104').first()
    if not user:
        print("User 7104 not found in database!")
        sys.exit(0)
    print(f"User: {user.name}")
    print(f"  id: {user.id}")
    print(f"  codigo_de_usuario: {user.codigo_de_usuario}")
    print(f"  is_active: {user.is_active}")
    print(f"  permissions: copier={user.func_copier}, copier_color={user.func_copier_color}, printer={user.func_printer}, printer_color={user.func_printer_color}, scanner={user.func_scanner}")
    
    assignments = db.query(UserPrinterAssignment).filter(UserPrinterAssignment.user_id == user.id).all()
    print(f"Assignments ({len(assignments)}):")
    for a in assignments:
        print(f"  - Printer IP: {a.printer.ip_address}")
        print(f"    is_active: {a.is_active}")
        print(f"    entry_index: {a.entry_index}")
        print(f"    permissions: copier={a.func_copier}, copier_color={a.func_copier_color}, printer={a.func_printer}, printer_color={a.func_printer_color}, scanner={a.func_scanner}")
finally:
    db.close()
