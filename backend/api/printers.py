"""
Printer management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.repository import PrinterRepository
from db.models import PrinterStatus
from .schemas import PrinterCreate, PrinterUpdate, PrinterResponse, MessageResponse

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
