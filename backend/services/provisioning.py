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
from services.encryption_service import EncryptionService
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
        printer_ids: List[int],
        reconcile: bool = True
    ) -> Dict:
        """
        Provision a user to multiple printers with intelligent retry logic.
        
        Args:
            db: Database session
            user_id: User ID to provision
            printer_ids: List of printer IDs to assign
            reconcile: If True, de-provisions the user from printers not in printer_ids
            
        Returns:
            Dict with provisioning results including overall_success, total_printers,
            successful_count, failed_count, results list, and summary_message
        """
        # Verify user exists
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Reconcile: identify active assignments in DB that are NOT in the new printer_ids list
        if reconcile:
            active_assignments = db.query(UserPrinterAssignment).filter(
                UserPrinterAssignment.user_id == user_id,
                UserPrinterAssignment.is_active == True
            ).all()
            
            active_printer_ids = {a.printer_id for a in active_assignments}
            new_printer_ids_set = set(printer_ids)
            
            printer_ids_to_remove = list(active_printer_ids - new_printer_ids_set)
            if printer_ids_to_remove:
                logger.info(f"🗑️ Reconciliando: desasignando usuario {user_id} de {len(printer_ids_to_remove)} impresoras desmarcadas: {printer_ids_to_remove}")
                ProvisioningService.remove_user_from_printers(db, user_id, printer_ids_to_remove)
            
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
        network_password = EncryptionService.decrypt(user.network_password_encrypted)
        
        # Build Ricoh payload
        ricoh_payload = {
            "nombre": user.name,
            "codigo_de_usuario": user.codigo_de_usuario,
            "nombre_usuario_inicio_sesion": user.network_username,
            "contrasena_inicio_sesion": network_password,
            "funciones_disponibles": {
                "copiadora": user.func_copier,
                "copiadora_color": user.func_copier_color,
                "impresora": user.func_printer,
                "impresora_color": user.func_printer_color,
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
        
        # Provision to each printer in parallel using a ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor
        from db.database import SessionLocal
        
        ricoh_client = get_ricoh_web_client()
        results = []
        busy_printers = []  # Lista de impresoras que están ocupadas
        
        logger.info(f"Starting parallel provisioning to {len(printers)} printer(s)...")
        
        def provision_worker(p):
            thread_db = SessionLocal()
            try:
                # Query fresh instances in this thread's session context
                thread_user = thread_db.query(User).filter(User.id == user_id).first()
                thread_printer = thread_db.query(Printer).filter(Printer.id == p.id).first()
                if not thread_user or not thread_printer:
                    return {
                        "printer_id": p.id,
                        "hostname": p.hostname,
                        "ip_address": p.ip_address,
                        "status": "failed",
                        "error_message": "User or printer not found in worker session",
                        "retry_attempts": 0,
                        "provisioned_at": None
                    }
                
                return ProvisioningService._provision_to_single_printer(
                    db=thread_db,
                    user=thread_user,
                    printer=thread_printer,
                    ricoh_payload=ricoh_payload,
                    ricoh_client=ricoh_client,
                    retry_strategy=retry_strategy
                )
            finally:
                thread_db.close()

        # Primera pasada: intentar todas las impresoras en paralelo
        with ThreadPoolExecutor(max_workers=min(len(printers), 10)) as executor:
            worker_results = list(executor.map(provision_worker, printers))
            
        for result in worker_results:
            # Si está BUSY, guardar para reintentar después
            if result['status'] == 'failed' and 'ocupada' in result.get('error_message', '').lower():
                # Encontrar la impresora correspondiente
                printer_obj = next((pr for pr in printers if pr.id == result['printer_id']), None)
                if printer_obj:
                    logger.info(f"⏸️  Impresora {printer_obj.hostname} está BUSY, se reintentará después")
                    busy_printers.append((printer_obj, result))
            else:
                results.append(result)
        
        # Segunda pasada: reintentar impresoras BUSY en paralelo
        if busy_printers:
            logger.info(f"🔄 Reintentando {len(busy_printers)} impresora(s) que estaban ocupadas...")
            time.sleep(10)  # Esperar 10 segundos antes de reintentar
            
            def busy_worker(p_and_res):
                p, _ = p_and_res
                return provision_worker(p)
                
            with ThreadPoolExecutor(max_workers=min(len(busy_printers), 10)) as executor:
                busy_results = list(executor.map(busy_worker, busy_printers))
                
            results.extend(busy_results)
        
        # Calculate summary
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'failed']
        
        from datetime import datetime
        
        return {
            "success": len(successful) > 0,
            "user_id": user.id,
            "user_name": user.name,
            "printers_provisioned": len(successful),
            "printer_ids": [r['printer_id'] for r in successful],
            "provisioned_at": datetime.now().isoformat(),
            "message": f"Usuario '{user.name}' provisionado exitosamente a {len(successful)}/{len(printers)} impresora(s)"
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
        if result is True or (isinstance(result, tuple) and result[0] is True):
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
            result = ricoh_client.provision_user(printer.ip_address, ricoh_payload, admin_password=printer.admin_password)
            
            # Classify error
            error_type = ProvisioningService._classify_provisioning_result(result)
            
            if error_type is None:
                # Success!
                elapsed = time.time() - start_time
                logger.info(f"✓ User provisioned to {printer.hostname} after {attempt} attempt(s) in {elapsed:.1f}s")
                
                # Extract entry_index if returned in success tuple
                entry_index = None
                if isinstance(result, tuple) and len(result) > 1:
                    entry_index = result[1]
                
                # Check if assignment already exists (even inactive ones)
                assignment = db.query(UserPrinterAssignment).filter(
                    and_(
                        UserPrinterAssignment.user_id == user.id,
                        UserPrinterAssignment.printer_id == printer.id
                    )
                ).first()
                
                permissions = {
                    'copiadora': user.func_copier,
                    'copiadora_color': user.func_copier_color,
                    'impresora': user.func_printer,
                    'impresora_color': user.func_printer_color,
                    'escaner': user.func_scanner,
                    'document_server': user.func_document_server,
                    'fax': user.func_fax,
                    'navegador': user.func_browser
                }
                
                has_active_permission = any(permissions.values())
                if assignment:
                    # Reactivate and update existing assignment
                    assignment.is_active = has_active_permission
                    if entry_index:
                        assignment.entry_index = entry_index
                    assignment.func_copier = permissions.get('copiadora', False)
                    assignment.func_copier_color = permissions.get('copiadora_color', False)
                    assignment.func_printer = permissions.get('impresora', False)
                    assignment.func_printer_color = permissions.get('impresora_color', False)
                    assignment.func_document_server = permissions.get('document_server', False)
                    assignment.func_fax = permissions.get('fax', False)
                    assignment.func_scanner = permissions.get('escaner', False)
                    assignment.func_browser = permissions.get('navegador', False)
                    if has_active_permission:
                        user.is_active = True
                    db.commit()
                    db.refresh(assignment)
                else:
                    # Create new assignment with entry_index and full permissions
                    AssignmentRepository.create(
                        db, 
                        user.id, 
                        printer.id, 
                        entry_index=entry_index,
                        permissions=permissions
                    )
                
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
            UserPrinterAssignment.user_id == user_id
        ).all()
        
        return {
            "user_id": user.id,
            "user_name": user.name,
            "codigo_de_usuario": user.codigo_de_usuario,
            "empresa": user.empresa,
            "centro_costos": user.centro_costos,
            "network_username": user.network_username,
            "smb_server": user.smb_server,
            "smb_port": user.smb_port,
            "smb_path": user.smb_path,
            "func_copier": user.func_copier,
            "func_copier_color": user.func_copier_color,
            "func_printer": user.func_printer,
            "func_printer_color": user.func_printer_color,
            "func_document_server": user.func_document_server,
            "func_fax": user.func_fax,
            "func_scanner": user.func_scanner,
            "func_browser": user.func_browser,
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
                        "copiadora_color": a.func_copier_color,
                        "impresora": a.func_printer,
                        "impresora_color": a.func_printer_color,
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
        Remove user permissions from specified printers (does not physically delete).
        Sets all permissions to False on both the physical printer and database assignment,
        and marks the assignment as inactive.
        
        Args:
            db: Database session
            user_id: User ID
            printer_ids: List of printer IDs to remove permissions from
            
        Returns:
            Dict with removal results
        """
        # Remove user from specified printers in parallel
        from concurrent.futures import ThreadPoolExecutor
        from db.database import SessionLocal
        
        removed_count = 0
        ricoh_client = get_ricoh_web_client()
        
        # Permisos para deshabilitar (Todo en False)
        disabled_permissions = {k: False for k in ['copiadora', 'copiadora_color', 'escaner', 'impresora', 'impresora_color', 'document_server', 'fax', 'navegador']}

        def remove_worker(printer_id):
            thread_db = SessionLocal()
            try:
                # 1. Obtener la asignación para tener el entry_index
                assignment = thread_db.query(UserPrinterAssignment).filter(
                    and_(
                        UserPrinterAssignment.user_id == user_id,
                        UserPrinterAssignment.printer_id == printer_id
                    )
                ).first()
                
                if assignment:
                    # 2. Deshabilitar todos los permisos en la impresora física
                    if assignment.entry_index:
                        printer = PrinterRepository.get_by_id(thread_db, printer_id)
                        if printer:
                            logger.info(f"🚫 Deshabilitando permisos físicamente para usuario {user_id} en impresora {printer.ip_address} (entry_index={assignment.entry_index})...")
                            ricoh_client.set_user_functions(
                                printer.ip_address, 
                                assignment.entry_index, 
                                disabled_permissions, 
                                admin_password=printer.admin_password,
                                set_password=False
                            )
                    else:
                        logger.warning(f"⚠️ Asignación sin entry_index para usuario {user_id} en impresora {printer_id}. Solo se actualizará en DB.")
                    
                    # 3. Eliminar físicamente la asignación de la base de datos al desasignar explícitamente
                    thread_db.delete(assignment)
                    thread_db.commit()
                    return True
                return False
            finally:
                thread_db.close()

        with ThreadPoolExecutor(max_workers=min(len(printer_ids), 10)) as executor:
            worker_results = list(executor.map(remove_worker, printer_ids))
            
        removed_count = sum(1 for r in worker_results if r)
        
        return {
            "success": True,
            "user_id": user_id,
            "printers_removed": removed_count,
            "message": f"Deshabilitados permisos de usuario en {removed_count} impresora(s)"
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
