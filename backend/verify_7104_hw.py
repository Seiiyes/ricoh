import sys
import os
import time
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify_7104_hw")

# Setup database context
from db.database import SessionLocal
from db import models
from db.repository import UserRepository, PrinterRepository, AssignmentRepository
from services.ricoh_web_client import get_ricoh_web_client
from services.provisioning import ProvisioningService

printer_ip = "192.168.91.252"
user_code = "7104"

def get_physical_permissions(client, printer_ip, entry_index, admin_password):
    """Fetch real permissions from physical printer using WIM client"""
    details = client._get_user_details(printer_ip, entry_index, fast_sync=False, admin_password=admin_password)
    if details:
        return details.get('permisos', {})
    return None

def main():
    db = SessionLocal()
    try:
        # 1. Fetch user and printer from DB
        user = db.query(models.User).filter(models.User.codigo_de_usuario == user_code).first()
        if not user:
            logger.error(f"User {user_code} not found in DB!")
            sys.exit(1)
        printer = PrinterRepository.get_by_ip(db, printer_ip)
        if not printer:
            logger.error(f"Printer {printer_ip} not found in DB!")
            sys.exit(1)
            
        logger.info(f"--- INITIAL STATE ---")
        logger.info(f"User: {user.name} (is_active: {user.is_active})")
        
        assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
        if assignment:
            logger.info(f"Assignment in DB exists: is_active={assignment.is_active}, entry_index={assignment.entry_index}")
            logger.info(f"DB Perms: copier={assignment.func_copier}, printer={assignment.func_printer}, scanner={assignment.func_scanner}")
        else:
            logger.info("No assignment in DB for this user/printer yet.")
            
        client = get_ricoh_web_client()
        
        # Verify physical presence
        logger.info("\nChecking physical user presence on printer...")
        phys_user = client.find_specific_user(printer_ip, user_code, admin_password=printer.admin_password)
        if phys_user:
            entry_index = phys_user.get('entry_index')
            logger.info(f"✅ User found physically on printer! entry_index={entry_index}")
            # Ensure assignment in DB has this entry_index
            if assignment and assignment.entry_index != entry_index:
                assignment.entry_index = entry_index
                db.commit()
        else:
            logger.info("❌ User not found physically on printer. Automatically provisioning user first...")
            # Provision the user to the printer (which will create the user and assignment)
            provision_res = ProvisioningService.provision_user_to_printers(db, user.id, [printer.id])
            logger.info(f"Provisioning result: {provision_res}")
            
            # Recheck physical presence
            phys_user = client.find_specific_user(printer_ip, user_code, admin_password=printer.admin_password)
            if phys_user:
                entry_index = phys_user.get('entry_index')
                logger.info(f"✅ User now found physically! entry_index={entry_index}")
                # Refresh assignment
                assignment = AssignmentRepository.get_by_user_and_printer(db, user.id, printer.id)
            else:
                logger.error("❌ Failed to find user physically even after provisioning!")
                sys.exit(1)
            
        entry_index = assignment.entry_index if assignment else entry_index
        
        # TEST 1: PROVISION WITH PERMISSIONS
        logger.info("\n--- TEST 1: Provisioning with active permissions ---")
        permissions = {
            'copiadora': True,
            'copiadora_color': False,
            'impresora': True,
            'impresora_color': False,
            'escaner': True,
            'document_server': False,
            'fax': False,
            'navegador': False
        }
        
        logger.info("Updating permissions in DB and physically on printer...")
        update_res = AssignmentRepository.update_assignment_state(
            db=db,
            user_id=user.id,
            printer_id=printer.id,
            permissions=permissions,
            entry_index=entry_index
        )
        
        # Push to physical printer
        sync_ok = client.set_user_functions(printer_ip, entry_index, permissions, admin_password=printer.admin_password)
        logger.info(f"Physical WIM update result: {sync_ok}")
        
        # Verify DB
        db.refresh(user)
        db.refresh(assignment)
        logger.info(f"DB User is_active: {user.is_active} (Expected: True)")
        logger.info(f"DB Assignment is_active: {assignment.is_active} (Expected: True)")
        
        # Verify physical printer
        phys_perms = get_physical_permissions(client, printer_ip, entry_index, printer.admin_password)
        logger.info(f"Physical printer permissions: {phys_perms}")
        logger.info(f"Matches DB: {phys_perms == permissions}")
        
        # TEST 2: SOFT-DEACTIVATION (ALL PERMISSIONS FALSE)
        logger.info("\n--- TEST 2: Soft-deactivating (removing all permissions) ---")
        logger.info("Calling ProvisioningService.remove_user_from_printers (which now soft-deactivates)...")
        remove_res = ProvisioningService.remove_user_from_printers(db, user.id, [printer.id])
        logger.info(f"Result: {remove_res}")
        
        # Verify DB
        db.refresh(user)
        db.refresh(assignment)
        logger.info(f"DB User is_active: {user.is_active} (Should remain True unless deleted globally)")
        logger.info(f"DB Assignment is_active: {assignment.is_active} (Expected: False)")
        logger.info(f"DB Assignment perms: copier={assignment.func_copier}, printer={assignment.func_printer}")
        
        # Verify physical printer
        phys_perms_after_remove = get_physical_permissions(client, printer_ip, entry_index, printer.admin_password)
        logger.info(f"Physical printer permissions: {phys_perms_after_remove}")
        expected_disabled = {k: False for k in permissions}
        # Only compare the keys we set
        is_disabled_ok = all(phys_perms_after_remove.get(k) is False for k in expected_disabled)
        logger.info(f"Are all physical permissions disabled? {is_disabled_ok}")
        
        # Verify physical presence (MUST STILL EXIST)
        phys_user_check = client.find_specific_user(printer_ip, user_code, admin_password=printer.admin_password)
        logger.info(f"Does user still exist physically in address book? {phys_user_check is not None} (Expected: True)")
        
        # TEST 3: REACTIVATION
        logger.info("\n--- TEST 3: Reactivation by assigning at least one permission ---")
        reactivate_permissions = {
            'copiadora': True,
            'copiadora_color': False,
            'impresora': False,
            'impresora_color': False,
            'escaner': False,
            'document_server': False,
            'fax': False,
            'navegador': False
        }
        logger.info("Updating DB and WIM with one active permission...")
        reactivate_res = AssignmentRepository.update_assignment_state(
            db=db,
            user_id=user.id,
            printer_id=printer.id,
            permissions=reactivate_permissions,
            entry_index=entry_index
        )
        # Push to physical printer
        sync_ok = client.set_user_functions(printer_ip, entry_index, reactivate_permissions, admin_password=printer.admin_password)
        logger.info(f"Physical WIM update result: {sync_ok}")
        
        # Verify DB
        db.refresh(user)
        db.refresh(assignment)
        logger.info(f"DB User is_active: {user.is_active} (Expected: True)")
        logger.info(f"DB Assignment is_active: {assignment.is_active} (Expected: True)")
        
        # Verify physical printer
        phys_perms_after_reactivate = get_physical_permissions(client, printer_ip, entry_index, printer.admin_password)
        logger.info(f"Physical printer permissions: {phys_perms_after_reactivate}")
        logger.info(f"Matches reactivate_permissions: {phys_perms_after_reactivate == reactivate_permissions}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
