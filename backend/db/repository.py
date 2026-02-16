"""
Repository pattern for database operations
Provides abstraction layer between API and database
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from .models import User, Printer, UserPrinterAssignment, PrinterStatus


class UserRepository:
    """Repository for User operations"""
    
    @staticmethod
    def create(db: Session, name: str, codigo_de_usuario: str, 
               network_username: str, network_password_encrypted: str,
               smb_server: str, smb_port: int, smb_path: str,
               func_copier: bool = False, func_printer: bool = False,
               func_document_server: bool = False, func_fax: bool = False,
               func_scanner: bool = False, func_browser: bool = False,
               email: Optional[str] = None, department: Optional[str] = None) -> User:
        """Create a new user with complete configuration"""
        user = User(
            name=name,
            codigo_de_usuario=codigo_de_usuario,
            network_username=network_username,
            network_password_encrypted=network_password_encrypted,
            smb_server=smb_server,
            smb_port=smb_port,
            smb_path=smb_path,
            func_copier=func_copier,
            func_printer=func_printer,
            func_document_server=func_document_server,
            func_fax=func_fax,
            func_scanner=func_scanner,
            func_browser=func_browser,
            email=email,
            department=department
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_codigo(db: Session, codigo_de_usuario: str) -> Optional[User]:
        """Get user by código de usuario"""
        return db.query(User).filter(User.codigo_de_usuario == codigo_de_usuario).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
        """Get all users with pagination"""
        query = db.query(User)
        if active_only:
            query = query.filter(User.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Delete user (soft delete by setting is_active=False)"""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False
    
    @staticmethod
    def search(db: Session, query: str) -> List[User]:
        """Search users by name or email"""
        search_pattern = f"%{query}%"
        return db.query(User).filter(
            or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).all()


class PrinterRepository:
    """Repository for Printer operations"""
    
    @staticmethod
    def create(db: Session, hostname: str, ip_address: str, **kwargs) -> Printer:
        """Create a new printer"""
        printer = Printer(
            hostname=hostname,
            ip_address=ip_address,
            **kwargs
        )
        db.add(printer)
        db.commit()
        db.refresh(printer)
        return printer
    
    @staticmethod
    def get_by_id(db: Session, printer_id: int) -> Optional[Printer]:
        """Get printer by ID"""
        return db.query(Printer).filter(Printer.id == printer_id).first()
    
    @staticmethod
    def get_by_ip(db: Session, ip_address: str) -> Optional[Printer]:
        """Get printer by IP address"""
        return db.query(Printer).filter(Printer.ip_address == ip_address).first()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Printer]:
        """Get all printers with pagination"""
        return db.query(Printer).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_status(db: Session, status: PrinterStatus) -> List[Printer]:
        """Get printers by status"""
        return db.query(Printer).filter(Printer.status == status).all()
    
    @staticmethod
    def update(db: Session, printer_id: int, **kwargs) -> Optional[Printer]:
        """Update printer fields"""
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if printer:
            for key, value in kwargs.items():
                if hasattr(printer, key):
                    setattr(printer, key, value)
            printer.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(printer)
        return printer
    
    @staticmethod
    def update_status(db: Session, printer_id: int, status: PrinterStatus) -> Optional[Printer]:
        """Update printer status and last_seen timestamp"""
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if printer:
            printer.status = status
            printer.last_seen = datetime.utcnow()
            db.commit()
            db.refresh(printer)
        return printer
    
    @staticmethod
    def update_toner_levels(db: Session, printer_id: int, cyan: int, magenta: int, 
                           yellow: int, black: int) -> Optional[Printer]:
        """Update toner levels"""
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if printer:
            printer.toner_cyan = cyan
            printer.toner_magenta = magenta
            printer.toner_yellow = yellow
            printer.toner_black = black
            db.commit()
            db.refresh(printer)
        return printer
    
    @staticmethod
    def delete(db: Session, printer_id: int) -> bool:
        """Delete printer"""
        printer = db.query(Printer).filter(Printer.id == printer_id).first()
        if printer:
            db.delete(printer)
            db.commit()
            return True
        return False
    
    @staticmethod
    def search(db: Session, query: str) -> List[Printer]:
        """Search printers by hostname, IP, or location"""
        search_pattern = f"%{query}%"
        return db.query(Printer).filter(
            or_(
                Printer.hostname.ilike(search_pattern),
                Printer.ip_address.ilike(search_pattern),
                Printer.location.ilike(search_pattern)
            )
        ).all()


class AssignmentRepository:
    """Repository for UserPrinterAssignment operations"""
    
    @staticmethod
    def create(db: Session, user_id: int, printer_id: int, notes: Optional[str] = None) -> UserPrinterAssignment:
        """Create a new assignment"""
        assignment = UserPrinterAssignment(
            user_id=user_id,
            printer_id=printer_id,
            notes=notes
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment
    
    @staticmethod
    def bulk_create(db: Session, user_id: int, printer_ids: List[int]) -> List[UserPrinterAssignment]:
        """Create multiple assignments for a user"""
        assignments = []
        for printer_id in printer_ids:
            # Check if assignment already exists
            existing = db.query(UserPrinterAssignment).filter(
                and_(
                    UserPrinterAssignment.user_id == user_id,
                    UserPrinterAssignment.printer_id == printer_id
                )
            ).first()
            
            if not existing:
                assignment = UserPrinterAssignment(
                    user_id=user_id,
                    printer_id=printer_id
                )
                db.add(assignment)
                assignments.append(assignment)
        
        db.commit()
        for assignment in assignments:
            db.refresh(assignment)
        return assignments
    
    @staticmethod
    def get_user_printers(db: Session, user_id: int) -> List[Printer]:
        """Get all printers assigned to a user"""
        assignments = db.query(UserPrinterAssignment).filter(
            UserPrinterAssignment.user_id == user_id,
            UserPrinterAssignment.is_active == True
        ).all()
        return [assignment.printer for assignment in assignments]
    
    @staticmethod
    def get_printer_users(db: Session, printer_id: int) -> List[User]:
        """Get all users assigned to a printer"""
        assignments = db.query(UserPrinterAssignment).filter(
            UserPrinterAssignment.printer_id == printer_id,
            UserPrinterAssignment.is_active == True
        ).all()
        return [assignment.user for assignment in assignments]
    
    @staticmethod
    def delete(db: Session, user_id: int, printer_id: int) -> bool:
        """Delete an assignment"""
        assignment = db.query(UserPrinterAssignment).filter(
            and_(
                UserPrinterAssignment.user_id == user_id,
                UserPrinterAssignment.printer_id == printer_id
            )
        ).first()
        
        if assignment:
            db.delete(assignment)
            db.commit()
            return True
        return False
    
    @staticmethod
    def delete_all_user_assignments(db: Session, user_id: int) -> int:
        """Delete all assignments for a user"""
        count = db.query(UserPrinterAssignment).filter(
            UserPrinterAssignment.user_id == user_id
        ).delete()
        db.commit()
        return count
