from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..api.endpoints.auth import get_current_user
from ..models.user import User
from ..models.rbac import Role, Permission

class RequiresPermission:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    def __call__(self, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # Check if the user has the required permission through their roles
        for role in current_user.roles:
            for perm in role.permissions:
                if perm.name == self.permission_name:
                    return True
        
        # Fallback to check default role names mapping (backward compatibility)
        if current_user.role == "Admin":
            return True
        elif current_user.role == "Scientist" and self.permission_name in ["run_queries", "edit_metadata", "export_data"]:
            return True
        elif current_user.role == "Reviewer" and self.permission_name in ["run_queries", "approve_data"]:
            return True
        elif current_user.role == "Compliance Officer" and self.permission_name in ["view_audit_trail"]:
            return True
            
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User does not have the required permission: {self.permission_name}"
        )
