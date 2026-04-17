from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from psycopg2.extras import RealDictCursor
from ..database import get_db
from .jwt_handler import verify_token

# Using the schema instead of the sqlalchemy model
from ..schemas.auth import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db=Depends(get_db)
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exception

    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT * FROM users WHERE username = %s LIMIT 1", (token_data.username,)
        )
        user = cursor.fetchone()
    finally:
        cursor.close()

    if user is None or not user["is_active"]:
        raise credentials_exception

    return UserOut(**user)


def require_roles(*roles: str):
    def role_checker(current_user: UserOut = Depends(get_current_user)) -> UserOut:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {list(roles)}",
            )
        return current_user

    return role_checker


# Convenience role guards
require_admin = require_roles("admin")
require_doctor = require_roles("admin", "doctor")
require_receptionist = require_roles("admin", "receptionist")
require_pharmacist = require_roles("admin", "pharmacist")
require_any_staff = require_roles("admin", "doctor", "receptionist", "pharmacist")
