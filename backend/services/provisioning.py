"""
Provisioning service for user-printer assignments
Handles bulk provisioning operations and communication with Ricoh printers
"""
from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import time

from db.repository import UserRepository, PrinterRepository, AssignmentRepository
from db.models import User, Printer
from services.encryption import get_encryption_service
from services.ricoh_web_client import get_ricoh_web_client

logger = logging.getLogger(__name__)


class ProvisioningService:
    """
    Service for provisioning users to printers
    """
    
    @staticmethod
    def provision_user_to_printers(
        db: Session,
        user_id: int,
        printer_ids: List[int]
    ) -> Dict:
        """
        Provision a user to multiple printers
        Sends complete user configuration to each Ricoh printer via SNMP
        
        Args:
            db: Database session
            user_id: User ID to provision
            printer_ids: List of printer IDs to assign
            
        Returns:
            Dict with provisioning results
        """
        # Verify user exists
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Verify all printers exist
        printers = []
        for printer_id in printer_ids:
            printer = PrinterRepository.get_by_id(db, printer_id)
            if not printer:
                raise ValueError(f"Printer with ID {printer_id} not found")
            printers.append(printer)
        
        # Decrypt password for provisioning
        encryption_service = get_encryption_service()
        network_password = encryption_service.decrypt(user.network_password_encrypted)
        
        # Build Ricoh payload
        ricoh_payload = {
            "nombre": user.name,
            "codigo_de_usuario": user.codigo_de_usuario,
            "nombre_usuario_inicio_sesion": user.network_username,
            "contrasena_inicio_sesion": network_password,
            "funciones_disponibles": {
                "copiadora": user.func_copier,
                "impresora": user.func_printer,
                "document_server": user.func_document_server,
                "fax": user.func_fax,
                "escaner": user.func_scanner,
                "navegador": user.func_browser
            },
            "carpeta_smb": {
                "protocolo": "SMB",
                "servidor": user.smb_server,
                "puerto": user.smb_port,
                "ruta": user.smb_path
            }
        }
        
        # Provision to each printer
        ricoh_client = get_ricoh_web_client()
        provisioned_count = 0
        errors = []
        
        print(f"\n🔄 Iniciando aprovisionamiento a {len(printers)} impresora(s)...")
        
        for printer in printers:
            try:
                print(f"\n📡 Provisionando a impresora:")
                print(f"   ID: {printer.id}")
                print(f"   IP: {printer.ip_address}")
                print(f"   Hostname: {printer.hostname}")
                
                logger.info(f"Provisioning user {user.name} to printer {printer.hostname} ({printer.ip_address})")
                
                # Retry logic for busy printers
                max_retries = 3
                retry_delay = 5  # seconds
                success = False
                
                for attempt in range(1, max_retries + 1):
                    if attempt > 1:
                        print(f"   🔄 Reintento {attempt}/{max_retries} (esperando {retry_delay}s...)")
                        time.sleep(retry_delay)
                    
                    # Send configuration to printer
                    result = ricoh_client.provision_user(printer.ip_address, ricoh_payload)
                    
                    if result is True:
                        success = True
                        break
                    elif result == "BUSY":
                        print(f"   ⏳ Impresora ocupada, reintentando...")
                        continue
                    else:
                        # Other error, don't retry
                        break
                
                print(f"   Resultado: {'✅ ÉXITO' if success else '❌ FALLO'}")
                
                if success:
                    # Create assignment in database
                    AssignmentRepository.create(db, user_id, printer.id)
                    provisioned_count += 1
                    logger.info(f"✓ User provisioned to {printer.hostname}")
                else:
                    errors.append(f"No se pudo provisionar a {printer.hostname} ({printer.ip_address})")
            except Exception as e:
                logger.error(f"Error provisioning to {printer.hostname}: {str(e)}")
                errors.append(f"Error en {printer.hostname}: {str(e)}")
        
        return {
            "success": provisioned_count > 0,
            "user_id": user_id,
            "user_name": user.name,
            "printers_provisioned": provisioned_count,
            "printer_ids": [p.id for p in printers[:provisioned_count]],
            "provisioned_at": datetime.utcnow().isoformat(),
            "message": f"Usuario '{user.name}' provisionado exitosamente a {provisioned_count}/{len(printers)} impresora(s)",
            "errors": errors if errors else None
        }
    
    @staticmethod
    def get_user_provisioning_status(db: Session, user_id: int) -> Dict:
        """
        Get provisioning status for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dict with user and assigned printers
        """
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        printers = AssignmentRepository.get_user_printers(db, user_id)
        
        return {
            "user_id": user.id,
            "user_name": user.name,
            "email": user.email,
            "smb_path": user.smb_path,
            "total_printers": len(printers),
            "printers": [
                {
                    "id": p.id,
                    "hostname": p.hostname,
                    "ip_address": p.ip_address,
                    "location": p.location,
                    "status": p.status.value
                }
                for p in printers
            ]
        }
    
    @staticmethod
    def remove_user_from_printers(
        db: Session,
        user_id: int,
        printer_ids: List[int]
    ) -> Dict:
        """
        Remove user from specified printers
        
        Args:
            db: Database session
            user_id: User ID
            printer_ids: List of printer IDs to remove from
            
        Returns:
            Dict with removal results
        """
        removed_count = 0
        for printer_id in printer_ids:
            if AssignmentRepository.delete(db, user_id, printer_id):
                removed_count += 1
        
        return {
            "success": True,
            "user_id": user_id,
            "printers_removed": removed_count,
            "message": f"Removed user from {removed_count} printer(s)"
        }
    
    @staticmethod
    def get_printer_users(db: Session, printer_id: int) -> Dict:
        """
        Get all users provisioned to a printer
        
        Args:
            db: Database session
            printer_id: Printer ID
            
        Returns:
            Dict with printer and assigned users
        """
        printer = PrinterRepository.get_by_id(db, printer_id)
        if not printer:
            raise ValueError(f"Printer with ID {printer_id} not found")
        
        users = AssignmentRepository.get_printer_users(db, printer_id)
        
        return {
            "printer_id": printer.id,
            "hostname": printer.hostname,
            "ip_address": printer.ip_address,
            "total_users": len(users),
            "users": [
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "department": u.department
                }
                for u in users
            ]
        }
