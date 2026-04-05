"""
Shared dependency for identifying the current user. 
The frontend must send the logged-in user's ID in the X-User-ID request header after a successful login.
"""

from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User


def get_current_user(
    x_user_id: int = Header(..., alias="X-User-ID", description="Logged-in user's ID"),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.user_id == x_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-User-ID header"
        )
    return user