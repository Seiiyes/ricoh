"""
Provisioning API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from services.provisioning import ProvisioningService
from .schemas import (
    ProvisionRequest,
    ProvisionResponse,
    UserProvisioningStatus,
    PrinterUsersResponse,
    MessageResponse
)

router = APIRouter(prefix="/provisioning", tags=["provisioning"])


@router.post("/provision", response_model=ProvisionResponse)
async def provision_user(
    provision_request: ProvisionRequest,
    db: Session = Depends(get_db)
):
    """
    Provision a user to multiple printers
    Creates assignments between user and printers
    """
    import logging
    logger = logging.getLogger(__name__)
    
    print("="*70)
    print("📥 PETICIÓN DE APROVISIONAMIENTO RECIBIDA")
    print(f"   User ID: {provision_request.user_id}")
    print(f"   Printer IDs: {provision_request.printer_ids}")
    print("="*70)
    
    logger.info(f"📥 Recibida petición de aprovisionamiento:")
    logger.info(f"   User ID: {provision_request.user_id}")
    logger.info(f"   Printer IDs: {provision_request.printer_ids}")
    logger.info(f"   Cantidad de impresoras: {len(provision_request.printer_ids)}")
    
    try:
        result = ProvisioningService.provision_user_to_printers(
            db,
            provision_request.user_id,
            provision_request.printer_ids
        )
        return ProvisionResponse(**result)
    except ValueError as e:
        logger.error(f"❌ Error de validación: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error durante aprovisionamiento: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Provisioning failed: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=UserProvisioningStatus)
async def get_user_provisioning(user_id: int, db: Session = Depends(get_db)):
    """
    Get provisioning status for a user
    Returns user info and all assigned printers
    """
    try:
        status_data = ProvisioningService.get_user_provisioning_status(db, user_id)
        return UserProvisioningStatus(**status_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provisioning status: {str(e)}"
        )


@router.get("/printer/{printer_id}", response_model=PrinterUsersResponse)
async def get_printer_users(printer_id: int, db: Session = Depends(get_db)):
    """
    Get all users provisioned to a printer
    """
    try:
        users_data = ProvisioningService.get_printer_users(db, printer_id)
        return PrinterUsersResponse(**users_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get printer users: {str(e)}"
        )


@router.delete("/remove", response_model=MessageResponse)
async def remove_user_from_printers(
    user_id: int,
    printer_ids: list[int],
    db: Session = Depends(get_db)
):
    """
    Remove user from specified printers
    """
    try:
        result = ProvisioningService.remove_user_from_printers(
            db,
            user_id,
            printer_ids
        )
        return MessageResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove assignments: {str(e)}"
        )
