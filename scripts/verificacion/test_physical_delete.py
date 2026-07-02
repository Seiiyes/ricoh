"""
Test physical deletion of user 7104 from printer 192.168.91.252 (entry_index=00089)
The user already has all permissions=False, so this is a safe physical removal test.
"""
import sys
sys.path.insert(0, '/app')

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

from services.ricoh_web_client import get_ricoh_web_client
from db.database import SessionLocal
from db import models
from db.repository import PrinterRepository, AssignmentRepository

# Test target
printer_ip = "192.168.91.252"
entry_index = "00089"
user_code = "7104"

db = SessionLocal()
try:
    printer = PrinterRepository.get_by_ip(db, printer_ip)
    if not printer:
        print(f"ERROR: Printer {printer_ip} not found in DB")
        sys.exit(1)
    
    user = db.query(models.User).filter(models.User.codigo_de_usuario == user_code).first()
    if not user:
        print(f"ERROR: User {user_code} not found in DB")
        sys.exit(1)
    
    print(f"Printer: {printer.hostname} @ {printer_ip}")
    print(f"User: {user.name} (code={user_code})")
    print(f"Entry index to delete: {entry_index}")
    
    # Check current DB assignment
    assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
    if assignment:
        print(f"DB Assignment ID={assignment.id}: copier={assignment.func_copier}, printer={assignment.func_printer}")
    
    print(f"\nAttempting PHYSICAL DELETION of user from printer...")
    
    client = get_ricoh_web_client()
    result = client.delete_user_from_printer(
        printer_ip, 
        entry_index, 
        admin_password=printer.admin_password
    )
    
    if result:
        print(f"✅ SUCCESS: User physically deleted from {printer_ip}!")
        
        # Now verify - try to find the user in the printer
        print(f"\nVerifying deletion by searching for user in printer...")
        user_check = client.find_specific_user(printer_ip, user_code, admin_password=printer.admin_password)
        if user_check:
            print(f"⚠️  WARNING: User STILL found in printer after deletion! entry_index={user_check.get('entry_index')}")
        else:
            print(f"✅ CONFIRMED: User no longer found in printer address book!")
        
        # Delete from DB too
        print(f"\nDeleting from DB...")
        AssignmentRepository.delete(db, user.id, printer.id)
        print(f"✅ DB assignment deleted")
    else:
        print(f"❌ FAILED: Physical deletion failed")
finally:
    db.close()
