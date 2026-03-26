"""
Printer management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

from db.database import get_db
from db.repository import PrinterRepository
from db.models import PrinterStatus, Printer
from db.models_auth import AdminUser
from .schemas import (
    PrinterCreate, 
    PrinterUpdate, 
    PrinterResponse,
    PrinterListResponse,
    MessageResponse,
    CapabilitiesResponse,
    CapabilitiesUpdate
)
from middleware.auth_middleware import get_current_user, get_client_ip, get_user_agent
from services.company_filter_service import CompanyFilterService
from services.audit_service import AuditService
from services.sanitization_service import SanitizationService

router = APIRouter(prefix="/printers", tags=["printers"])


@router.post("/", response_model=PrinterResponse, status_code=status.HTTP_201_CREATED)
async def create_printer(
    request: Request,
    printer: PrinterCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new printer (manual registration)
    
    Requires authentication. Admin users can only create printers for their empresa.
    """
    # Sanitizar inputs de texto
    sanitized_hostname = SanitizationService.sanitize_string(printer.hostname)
    sanitized_ip = SanitizationService.sanitize_string(printer.ip_address)
    sanitized_location = SanitizationService.sanitize_string(printer.location) if printer.location else None
    sanitized_model = SanitizationService.sanitize_string(printer.detected_model) if printer.detected_model else None
    sanitized_serial = SanitizationService.sanitize_string(printer.serial_number) if printer.serial_number else None
    
    # Check if IP already exists
    existing = PrinterRepository.get_by_ip(db, sanitized_ip)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Printer with IP {sanitized_ip} already exists"
        )
    
    # Enforce empresa_id for admin users
    printer_data = printer.dict()
    printer_data['hostname'] = sanitized_hostname
    printer_data['ip_address'] = sanitized_ip
    printer_data['location'] = sanitized_location
    printer_data['detected_model'] = sanitized_model
    printer_data['serial_number'] = sanitized_serial
    printer_data = CompanyFilterService.enforce_company_on_create(current_user, printer_data)
    
    try:
        new_printer = PrinterRepository.create(
            db,
            hostname=printer_data.get('hostname'),
            ip_address=printer_data.get('ip_address'),
            location=printer_data.get('location'),
            empresa_id=printer_data.get('empresa_id'),
            detected_model=printer_data.get('detected_model'),
            serial_number=printer_data.get('serial_number'),
            has_color=printer_data.get('has_color'),
            has_scanner=printer_data.get('has_scanner'),
            has_fax=printer_data.get('has_fax'),
            toner_cyan=printer_data.get('toner_cyan'),
            toner_magenta=printer_data.get('toner_magenta'),
            toner_yellow=printer_data.get('toner_yellow'),
            toner_black=printer_data.get('toner_black'),
            status=PrinterStatus.ONLINE
        )
        
        # Log audit
        AuditService.log_action(
            db=db,
            user=current_user,
            accion="crear",
            modulo="printers",
            resultado=AuditService.RESULTADO_EXITO,
            entidad_tipo="printer",
            entidad_id=new_printer.id,
            detalles={"hostname": new_printer.hostname, "ip_address": new_printer.ip_address},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return new_printer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create printer: {str(e)}"
        )


@router.get("/", response_model=PrinterListResponse)
async def get_printers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: str = None,
    search: Optional[str] = Query(None, description="Search by hostname or IP"),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all printers with pagination and optional filters
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **status_filter**: Filter by status (online, offline, error, unknown)
    - **search**: Search term for hostname or IP address
    
    Requires authentication. Admin users only see printers from their empresa.
    """
    # Build base query
    query = db.query(Printer)
    
    # Apply company filter
    query = CompanyFilterService.apply_filter(query, current_user)
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Printer.hostname.ilike(search_pattern),
                Printer.ip_address.ilike(search_pattern),
                Printer.location.ilike(search_pattern)
            )
        )
    
    # Apply status filter if provided
    if status_filter:
        try:
            status_enum = PrinterStatus(status_filter)
            query = query.filter(Printer.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    
    # Get paginated results
    printers = query.order_by(Printer.hostname).offset(offset).limit(page_size).all()
    
    return PrinterListResponse(
        items=[PrinterResponse.model_validate(p) for p in printers],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{printer_id}", response_model=PrinterResponse)
async def get_printer(
    printer_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get printer by ID
    
    Requires authentication. Admin users can only access printers from their empresa.
    """
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Validate company access
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this printer"
        )
    
    return printer


@router.put("/{printer_id}", response_model=PrinterResponse)
async def update_printer(
    request: Request,
    printer_id: int,
    printer_update: PrinterUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update printer information
    
    Requires authentication. Admin users can only update printers from their empresa.
    """
    # Check if printer exists
    existing_printer = PrinterRepository.get_by_id(db, printer_id)
    if not existing_printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Validate company access
    if not CompanyFilterService.validate_company_access(current_user, existing_printer.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this printer"
        )
    
    # Update only provided fields
    update_data = printer_update.dict(exclude_unset=True)
    
    try:
        updated_printer = PrinterRepository.update(db, printer_id, **update_data)
        
        # Log audit
        AuditService.log_action(
            db=db,
            user=current_user,
            accion="editar",
            modulo="printers",
            resultado=AuditService.RESULTADO_EXITO,
            entidad_tipo="printer",
            entidad_id=printer_id,
            detalles={"hostname": updated_printer.hostname, "updated_fields": list(update_data.keys())},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return updated_printer
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error updating printer {printer_id}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Update data: {update_data}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update printer: {str(e)}"
        )


@router.delete("/{printer_id}", response_model=MessageResponse)
async def delete_printer(
    request: Request,
    printer_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete printer
    
    Requires authentication. Admin users can only delete printers from their empresa.
    """
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Validate company access
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this printer"
        )
    
    success = PrinterRepository.delete(db, printer_id)
    if success:
        # Log audit
        AuditService.log_action(
            db=db,
            user=current_user,
            accion="eliminar",
            modulo="printers",
            resultado=AuditService.RESULTADO_EXITO,
            entidad_tipo="printer",
            entidad_id=printer_id,
            detalles={"hostname": printer.hostname},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return MessageResponse(
            success=True,
            message=f"Printer '{printer.hostname}' deleted successfully"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete printer"
        )


@router.get("/search/{query}", response_model=List[PrinterResponse])
async def search_printers(
    query: str,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search printers by hostname, IP, or location
    
    Requires authentication. Admin users only see printers from their empresa.
    """
    # Build base query for search
    base_query = db.query(Printer)
    
    # Apply company filter
    base_query = CompanyFilterService.apply_filter(base_query, current_user)
    
    # Apply search filter
    search_pattern = f"%{query}%"
    from sqlalchemy import or_
    printers = base_query.filter(
        or_(
            Printer.hostname.ilike(search_pattern),
            Printer.ip_address.ilike(search_pattern),
            Printer.location.ilike(search_pattern)
        )
    ).all()
    
    return printers



# ============================================================================
# Printer Capabilities Endpoints
# ============================================================================

@router.get("/{printer_id}/capabilities", response_model=CapabilitiesResponse)
async def get_printer_capabilities(
    printer_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get printer capabilities
    
    Returns the detected or manually configured capabilities for a printer.
    If no capabilities are set, returns safe defaults (all features enabled).
    
    Requires authentication. Admin users can only access printers from their empresa.
    """
    from models.capabilities import Capabilities
    
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Validate company access
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this printer"
        )
    
    # Get capabilities or return safe defaults
    if printer.capabilities_json:
        return CapabilitiesResponse(**printer.capabilities_json)
    else:
        # Return safe defaults (show all columns for backward compatibility)
        default_caps = Capabilities.create_default()
        return CapabilitiesResponse(**default_caps.to_json())


@router.put("/{printer_id}/capabilities", response_model=CapabilitiesResponse)
async def update_printer_capabilities(
    request: Request,
    printer_id: int,
    capabilities_update: CapabilitiesUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update printer capabilities manually
    
    This endpoint allows manual configuration of printer capabilities.
    Sets manual_override=True to prevent automatic detection from overwriting.
    
    Requires authentication. Admin users can only update printers from their empresa.
    """
    from models.capabilities import Capabilities
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Validate company access
    if not CompanyFilterService.validate_company_access(current_user, printer.empresa_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this printer"
        )
    
    try:
        # Get current capabilities or create defaults
        if printer.capabilities_json:
            current_caps = Capabilities.from_json(printer.capabilities_json)
        else:
            current_caps = Capabilities.create_default()
        
        # Update only provided fields
        update_data = capabilities_update.dict(exclude_unset=True)
        
        # Create updated capabilities
        updated_caps_dict = current_caps.to_json()
        updated_caps_dict.update(update_data)
        updated_caps_dict['detected_at'] = datetime.utcnow().isoformat() + 'Z'
        updated_caps_dict['manual_override'] = True
        
        # Validate and create Capabilities object
        updated_caps = Capabilities(**updated_caps_dict)
        
        # Update printer
        printer.update_capabilities(updated_caps.to_json(), manual=True)
        db.commit()
        db.refresh(printer)
        
        # Log the manual update
        logger.info(
            f"Manual capabilities update for printer {printer_id} ({printer.hostname}): "
            f"{update_data}"
        )
        
        # Log audit
        AuditService.log_action(
            db=db,
            user=current_user,
            accion="editar_capacidades",
            modulo="printers",
            resultado=AuditService.RESULTADO_EXITO,
            entidad_tipo="printer",
            entidad_id=printer_id,
            detalles={"hostname": printer.hostname, "updated_capabilities": update_data},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        return CapabilitiesResponse(**printer.capabilities_json)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating capabilities for printer {printer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update capabilities: {str(e)}"
        )
