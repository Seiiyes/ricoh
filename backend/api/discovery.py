"""
Network discovery API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os

from db.database import get_db
from db.repository import PrinterRepository
from db.models import PrinterStatus
from services.network_scanner import NetworkScanner
from services.snmp_client import get_snmp_client
from .schemas import ScanRequest, ScanResponse, DiscoveredDevice, MessageResponse

router = APIRouter(prefix="/discovery", tags=["discovery"])


@router.post("/scan", response_model=ScanResponse)
async def scan_network_endpoint(scan_request: ScanRequest, db: Session = Depends(get_db)):
    """
    Scan network for Ricoh printers
    
    Performs real network scan - no demo mode
    """
    start_time = datetime.now()
    
    try:
        # Always perform actual network scan
        scanner = NetworkScanner(timeout=1.0)
        devices_data = await scanner.scan_network(scan_request.ip_range, max_concurrent=50)
        
        # Calculate total IPs scanned
        import ipaddress
        network = ipaddress.ip_network(scan_request.ip_range, strict=False)
        total_scanned = network.num_addresses - 2
        
        # Convert to response schema
        devices = [DiscoveredDevice(**device) for device in devices_data]
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return ScanResponse(
            devices=devices,
            total_scanned=total_scanned,
            total_found=len(devices),
            scan_duration_seconds=round(duration, 2),
            timestamp=datetime.now()
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scan failed: {str(e)}"
        )


@router.post("/register-discovered", response_model=MessageResponse)
async def register_discovered_printers(
    devices: list[DiscoveredDevice],
    db: Session = Depends(get_db)
):
    """
    Register discovered printers to database
    Skips printers that already exist (by IP)
    """
    registered_count = 0
    skipped_count = 0
    errors = []
    
    for device in devices:
        try:
            # Check if printer already exists
            existing = PrinterRepository.get_by_ip(db, device.ip_address)
            if existing:
                skipped_count += 1
                continue
            
            # Create new printer
            PrinterRepository.create(
                db,
                hostname=device.hostname,
                ip_address=device.ip_address,
                location=device.location,
                detected_model=device.detected_model,
                has_color=device.has_color,
                has_scanner=device.has_scanner,
                has_fax=device.has_fax,
                toner_cyan=device.toner_cyan,
                toner_magenta=device.toner_magenta,
                toner_yellow=device.toner_yellow,
                toner_black=device.toner_black,
                status=PrinterStatus(device.status)
            )
            registered_count += 1
            
        except Exception as e:
            errors.append(f"Failed to register {device.ip_address}: {str(e)}")
    
    message = f"Registered {registered_count} printer(s), skipped {skipped_count} existing"
    if errors:
        message += f". Errors: {'; '.join(errors)}"
    
    return MessageResponse(
        success=True,
        message=message
    )


@router.post("/refresh-snmp/{printer_id}", response_model=MessageResponse)
async def refresh_printer_snmp(
    printer_id: int,
    db: Session = Depends(get_db)
):
    """
    Refresh printer information via SNMP
    Updates toner levels, model, serial number, etc.
    
    Note: Currently SNMP is disabled, returns informational message
    """
    # Get printer from database
    printer = PrinterRepository.get_by_id(db, printer_id)
    if not printer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Printer with ID {printer_id} not found"
        )
    
    # Check if SNMP is available
    snmp_client = get_snmp_client()
    if not snmp_client:
        return MessageResponse(
            success=False,
            message="SNMP functionality is currently disabled. Printer data cannot be refreshed automatically."
        )
    
    try:
        # Query SNMP
        snmp_info = await snmp_client.get_printer_info(printer.ip_address)
        
        # Update printer with SNMP data
        update_data = {}
        
        if snmp_info.model:
            update_data['detected_model'] = snmp_info.model
        if snmp_info.serial_number:
            update_data['serial_number'] = snmp_info.serial_number
        if snmp_info.location:
            update_data['location'] = snmp_info.location
        
        # Update toner levels
        if snmp_info.toner_black is not None:
            update_data['toner_black'] = snmp_info.toner_black
        if snmp_info.toner_cyan is not None:
            update_data['toner_cyan'] = snmp_info.toner_cyan
        if snmp_info.toner_magenta is not None:
            update_data['toner_magenta'] = snmp_info.toner_magenta
        if snmp_info.toner_yellow is not None:
            update_data['toner_yellow'] = snmp_info.toner_yellow
        
        # Update in database
        if update_data:
            PrinterRepository.update(db, printer_id, **update_data)
            return MessageResponse(
                success=True,
                message=f"Printer {printer.hostname} updated via SNMP"
            )
        else:
            return MessageResponse(
                success=False,
                message="No SNMP data available for this printer"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SNMP query failed: {str(e)}"
        )
