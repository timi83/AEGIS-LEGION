
from fastapi import Depends, HTTPException, status
from src.routes.auth import get_current_user
from src.models.user import User

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return user

# Pre-defined dependencies
admin_only = RoleChecker(["admin"])
analyst_access = RoleChecker(["admin", "analyst"])
viewer_access = RoleChecker(["admin", "analyst", "viewer"])
