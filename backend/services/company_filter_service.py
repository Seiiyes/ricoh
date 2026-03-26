"""
Company Filter Service
Servicio para filtrado automático por empresa según rol (multi-tenancy)
"""
from sqlalchemy.orm import Query
from typing import Dict, Any

from db.models_auth import AdminUser


class CompanyFilterService:
    """Service for automatic company filtering based on user role"""
    
    @classmethod
    def apply_filter(cls, query: Query, user: AdminUser, empresa_field: str = "empresa_id") -> Query:
        """
        Apply company filter to SQLAlchemy query
        
        Logic:
            - If user.rol == "superadmin": No filter (return all)
            - If user.rol in ["admin", "viewer", "operator"]: Filter by user.empresa_id
        
        Args:
            query: SQLAlchemy query
            user: Authenticated user
            empresa_field: Name of the empresa_id field in the model (default: "empresa_id")
            
        Returns:
            Filtered query
            
        Example:
            >>> query = db.query(Printer)
            >>> filtered_query = CompanyFilterService.apply_filter(query, current_user)
            >>> printers = filtered_query.all()
        """
        # Superadmin sees everything
        if user.is_superadmin():
            return query
        
        # Other roles only see their company's data
        # Get the model from the query
        model = query.column_descriptions[0]['entity']
        
        # Apply filter using the empresa_field
        return query.filter(getattr(model, empresa_field) == user.empresa_id)
    
    @classmethod
    def validate_company_access(cls, user: AdminUser, empresa_id: int) -> bool:
        """
        Validate if user can access empresa
        
        Returns:
            True if superadmin or empresa_id matches user.empresa_id
            
        Example:
            >>> can_access = CompanyFilterService.validate_company_access(current_user, 1)
            >>> if not can_access:
            ...     raise HTTPException(status_code=403, detail="Access denied")
        """
        # Superadmin can access any empresa
        if user.is_superadmin():
            return True
        
        # Other roles can only access their own empresa
        return user.empresa_id == empresa_id
    
    @classmethod
    def enforce_company_on_create(cls, user: AdminUser, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce empresa_id on resource creation
        
        Logic:
            - If user.rol == "superadmin": Allow any empresa_id (or use provided)
            - If user.rol == "admin": Force empresa_id = user.empresa_id (ignore provided)
        
        Args:
            user: Authenticated user
            data: Data dictionary for resource creation
            
        Returns:
            Modified data dictionary with enforced empresa_id
            
        Example:
            >>> data = {"name": "Printer 1", "empresa_id": 999}
            >>> data = CompanyFilterService.enforce_company_on_create(admin_user, data)
            >>> # If admin_user.empresa_id = 1, data["empresa_id"] will be 1 (not 999)
        """
        # Superadmin can create resources for any empresa
        if user.is_superadmin():
            return data
        
        # Admin can only create resources for their own empresa
        # Force empresa_id to user's empresa_id (ignore any provided value)
        data_copy = data.copy()
        data_copy['empresa_id'] = user.empresa_id
        
        return data_copy
    
    @classmethod
    def get_accessible_empresa_ids(cls, user: AdminUser) -> list[int]:
        """
        Get list of empresa IDs that user can access
        
        Returns:
            List of empresa IDs (empty list for superadmin means "all")
            
        Example:
            >>> empresa_ids = CompanyFilterService.get_accessible_empresa_ids(current_user)
            >>> if empresa_ids:  # Not superadmin
            ...     query = query.filter(Printer.empresa_id.in_(empresa_ids))
        """
        # Superadmin can access all empresas (return empty list as indicator)
        if user.is_superadmin():
            return []
        
        # Other roles can only access their own empresa
        if user.empresa_id:
            return [user.empresa_id]
        
        return []
    
    @classmethod
    def filter_response_list(cls, user: AdminUser, items: list, empresa_field: str = "empresa_id") -> list:
        """
        Filter a list of items by empresa_id (for in-memory filtering)
        
        Args:
            user: Authenticated user
            items: List of items (dicts or objects)
            empresa_field: Name of the empresa_id field
            
        Returns:
            Filtered list
            
        Example:
            >>> items = [{"id": 1, "empresa_id": 1}, {"id": 2, "empresa_id": 2}]
            >>> filtered = CompanyFilterService.filter_response_list(admin_user, items)
        """
        # Superadmin sees everything
        if user.is_superadmin():
            return items
        
        # Filter items by empresa_id
        filtered_items = []
        for item in items:
            # Handle both dict and object
            if isinstance(item, dict):
                item_empresa_id = item.get(empresa_field)
            else:
                item_empresa_id = getattr(item, empresa_field, None)
            
            if item_empresa_id == user.empresa_id:
                filtered_items.append(item)
        
        return filtered_items
