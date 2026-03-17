"""
Provisioning service for user-printer assignments
Handles bulk provisioning operations and communication with Ricoh printers
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import time

from db.repository import UserRepository, PrinterRepository, AssignmentRepository
from db.models import User, Printer, UserPrinterAssignment
from sqlalchemy import and_
from services.encryption import get_encryption_service
from services.ricoh_web_client import get_ricoh_web_client
from services.retry_strategy import RetryStrategy, load_retry_config_from_env, ErrorType

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
        Provision a user to multiple printers with intelligent retry logic.
        
        Args:
            db: Database session
            user_id: User ID to provision
            printer_ids: List of printer IDs to assign
            
        Returns:
            Dict with provisioning results including overall_success, total_printers,
            successful_count, failed_count, results list, and summary_message
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
        
        # Initialize retry strategy
        retry_config = load_retry_config_from_env()
        retry_strategy = RetryStrategy(retry_config)
        
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
        
        # Provision to each printer sequentially
        ricoh_client = get_ricoh_web_client()
        results = []
        
        logger.info(f"Starting provisioning to {len(printers)} printer(s)...")
        
        for printer in printers:
            result = ProvisioningService._provision_to_single_printer(
                db=db,
                user=user,
                printer=printer,
                ricoh_payload=ricoh_payload,
                ricoh_client=ricoh_client,
                retry_strategy=retry_strategy
            )
            results.append(result)
        
        # Calculate summary
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']
        
        return {
            "overall_success": len(successful) > 0,
            "total_printers": len(printers),
            "successful_count": len(successful),
            "failed_count": len(failed),
            "results": results,
            "summary_message": f"Usuario '{user.name}' provisionado exitosamente a {len(successful)}/{len(printers)} impresora(s)"
        }
    
    @staticmethod
    def _classify_provisioning_result(result) -> Optional[ErrorType]:
        """
        Classify provisioning result into error type.
        
        Args:
            result: Return value from ricoh_client.provision_user()
            
        Returns:
            ErrorType if error, None if success
        """
        if result is True:
            return None  # Success
        elif result == "BUSY":
            return 'BUSY'
        elif result == "BADFLOW":
            return 'BADFLOW'
        elif result == "TIMEOUT":
            return 'TIMEOUT'
        elif result == "CONNECTION":
            return 'CONNECTION'
        else:
            return 'OTHER'  # Generic failure
    
    @staticmethod
    def _format_error_message(error_type: ErrorType, result=None) -> str:
        """Format user-friendly error message in Spanish"""
        messages = {
            'BUSY': 'La impresora está ocupada. El dispositivo está siendo utilizado por otras funciones.',
            'BADFLOW': 'Error de protección anti-scraping. La sesión con la impresora es inválida.',
            'TIMEOUT': 'Tiempo de espera agotado al conectar con la impresora.',
            'CONNECTION': 'No se pudo conectar con la impresora.',
            'OTHER': 'Error desconocido durante el aprovisionamiento.'
        }
        return messages.get(error_type, 'Error desconocido')
    
    @staticmethod
    def _provision_to_single_printer(
        db: Session,
        user,
        printer,
        ricoh_payload: Dict,
        ricoh_client,
        retry_strategy: RetryStrategy
    ) -> Dict:
        """
        Provision user to a single printer with retry logic.
        
        Returns:
            Dict with printer_id, hostname, ip_address, status, error_message, retry_attempts, provisioned_at
        """
        logger.info(f"Provisioning user {user.name} to printer {printer.hostname} ({printer.ip_address})")
        
        start_time = time.time()
        attempt = 0
        last_error_type = None
        
        while True:
            attempt += 1
            logger.info(f"Attempt {attempt} for printer {printer.ip_address}")
            
            # Attempt provisioning
            result = ricoh_client.provision_user(printer.ip_address, ricoh_payload)
            
            # Classify error
            error_type = ProvisioningService._classify_provisioning_result(result)
            
            if error_type is None:
                # Success!
                elapsed = time.time() - start_time
                logger.info(f"✓ User provisioned to {printer.hostname} after {attempt} attempt(s) in {elapsed:.1f}s")
                
                # Create assignment in database
                AssignmentRepository.create(db, user.id, printer.id)
                
                return {
                    "printer_id": printer.id,
                    "hostname": printer.hostname,
                    "ip_address": printer.ip_address,
                    "status": "success",
                    "error_message": None,
                    "retry_attempts": attempt - 1,
                    "provisioned_at": datetime.utcnow().isoformat()
                }
            
            # Handle BADFLOW with session reset
            if error_type == 'BADFLOW' and attempt == 1:
                logger.warning(f"BADFLOW detected, resetting session...")
                ricoh_client.reset_session()
            
            # Check if should retry
            should_retry, delay = retry_strategy.should_retry(error_type, attempt)
            
            if not should_retry:
                elapsed = time.time() - start_time
                error_msg = ProvisioningService._format_error_message(error_type, result)
                logger.error(f"✗ Provisioning failed to {printer.hostname} after {attempt} attempts in {elapsed:.1f}s: {error_msg}")
                
                return {
                    "printer_id": printer.id,
                    "hostname": printer.hostname,
                    "ip_address": printer.ip_address,
                    "status": "failed",
                    "error_message": error_msg,
                    "retry_attempts": attempt - 1,
                    "provisioned_at": None
                }
            
            # Wait before retry
            if delay > 0:
                logger.info(f"Waiting {delay}s before retry...")
                time.sleep(delay)
    
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
        
        # Obtener las asignaciones directamente para acceder a sus metadatos (permisos por impresora)
        assignments = db.query(UserPrinterAssignment).filter(
            UserPrinterAssignment.user_id == user_id,
            UserPrinterAssignment.is_active == True
        ).all()
        
        return {
            "user_id": user.id,
            "user_name": user.name,
            "empresa": user.empresa,
            "smb_path": user.smb_path,
            "total_printers": len(assignments),
            "printers": [
                {
                    "id": a.printer.id,
                    "hostname": a.printer.hostname,
                    "ip_address": a.printer.ip_address,
                    "location": a.printer.location,
                    "status": a.printer.status.value,
                    "entry_index": a.entry_index,
                    "permisos": {
                        "copiadora": a.func_copier,
                        "impresora": a.func_printer,
                        "document_server": a.func_document_server,
                        "fax": a.func_fax,
                        "escaner": a.func_scanner,
                        "navegador": a.func_browser
                    }
                }
                for a in assignments
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
        ricoh_client = get_ricoh_web_client()
        
        # Permisos para deshabilitar (Todo en False)
        disabled_permissions = {k: False for k in ['copiadora', 'escaner', 'impresora', 'document_server', 'fax', 'navegador']}

        for printer_id in printer_ids:
            # 1. Obtener la asignación para tener el entry_index
            assignment = db.query(UserPrinterAssignment).filter(
                and_(
                    UserPrinterAssignment.user_id == user_id,
                    UserPrinterAssignment.printer_id == printer_id
                )
            ).first()
            
            if assignment and assignment.entry_index:
                # 2. Intentar deshabilitar en el hardware
                printer = PrinterRepository.get_by_id(db, printer_id)
                if printer:
                    logger.info(f"🚫 Deshabilitando funciones de usuario {user_id} en impresora {printer.ip_address}...")
                    ricoh_client.set_user_functions(printer.ip_address, assignment.entry_index, disabled_permissions)
            
            # 3. Eliminar de la base de datos
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
                    "empresa": u.empresa,
                    "centro_costos": u.centro_costos
                }
                for u in users
            ]
        }
