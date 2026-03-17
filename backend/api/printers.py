"""
Printer management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.repository import PrinterRepository
from db.models import PrinterStatus
from .schemas import (
    PrinterCreate, 
    PrinterUpdate, 
    PrinterResponse, 
    MessageResponse,
    CapabilitiesResponse,
    CapabilitiesUpdate
)

router = APIRouter(prefix="/printers", tags=["printers"])


@router.post("/", response_model=PrinterResponse, status_code=status.HTTP_201_CREATED)
async def create_printer(printer: PrinterCreate, db: Session = Depends(get_db)):
    """
    Create a new printer (manual registration)
    """
    # Check if IP already exists
    existing = PrinterRepository.get_by_ip(db, printer.ip_address)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Printer with IP {printer.ip_address} already exists"
        )
    
    try:
        new_printer = PrinterRepository.create(
            db,
            hostname=printer.hostname,
            ip_address=printer.ip_address,
            location=printer.location,
            detected_model=printer.detected_model,
            serial_number=printer.serial_number,
            has_color=printer.has_color,
            has_scanner=printer.has_scanner,
            has_fax=printer.has_fax,
            toner_cyan=printer.toner_cyan,
            toner_magenta=printer.toner_magenta,
            toner_yellow=printer.toner_yellow,
            toner_black=printer.toner_black,
            status=PrinterStatus.ONLINE
        )
        return new_printer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create printer: {str(e)}"
        )


@router.get("/", response_model=List[PrinterResponse])
async def get_printers(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all printers with pagination and optional status filter
    """
    if status_filter:
        try:
            status_enum = PrinterStatus(status_filter)
            printers = PrinterRepository.get_by_status(db, status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    else:
        printers = PrinterRepository.get_all(db, skip=skip, limit=limit)
    
    return printers


@router.get("/{printer_id}", response_model=PrinterResponse)
async def get_printer(printer_id: int, db: Session = Depends(get_db)):
    """
    Get printer by ID
    """
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    return printer


@router.put("/{printer_id}", response_model=PrinterResponse)
async def update_printer(
    printer_id: int,
    printer_update: PrinterUpdate,
    db: Session = Depends(get_db)
):
    """
    Update printer information
    """
    # Check if printer exists
    existing_printer = PrinterRepository.get_by_id(db, printer_id)
    if not existing_printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Update only provided fields
    update_data = printer_update.dict(exclude_unset=True)
    
    try:
        updated_printer = PrinterRepository.update(db, printer_id, **update_data)
        return updated_printer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update printer: {str(e)}"
        )


@router.delete("/{printer_id}", response_model=MessageResponse)
async def delete_printer(printer_id: int, db: Session = Depends(get_db)):
    """
    Delete printer
    """
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    success = PrinterRepository.delete(db, printer_id)
    if success:
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
async def search_printers(query: str, db: Session = Depends(get_db)):
    """
    Search printers by hostname, IP, or location
    """
    printers = PrinterRepository.search(db, query)
    return printers



# ============================================================================
# Printer Capabilities Endpoints
# ============================================================================

@router.get("/{printer_id}/capabilities", response_model=CapabilitiesResponse)
async def get_printer_capabilities(printer_id: int, db: Session = Depends(get_db)):
    """
    Get printer capabilities
    
    Returns the detected or manually configured capabilities for a printer.
    If no capabilities are set, returns safe defaults (all features enabled).
    """
    from models.capabilities import Capabilities
    
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
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
    printer_id: int,
    capabilities_update: CapabilitiesUpdate,
    db: Session = Depends(get_db)
):
    """
    Update printer capabilities manually
    
    This endpoint allows manual configuration of printer capabilities.
    Sets manual_override=True to prevent automatic detection from overwriting.
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
        
        return CapabilitiesResponse(**printer.capabilities_json)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating capabilities for printer {printer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update capabilities: {str(e)}"
        )
