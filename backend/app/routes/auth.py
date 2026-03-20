from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.user import User
from app.models.user import Role
from app.models.user import Designation
from app.core.security import verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =========================
# REQUEST SCHEMA
# =========================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# =========================
# RESPONSE SCHEMA
# =========================
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    designation: str | None = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


# =========================
# LOGIN API
# =========================
@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Fetch role & designation
    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    designation = None

    if user.designation_id:
        designation = db.query(Designation).filter(
            Designation.designation_id == user.designation_id
        ).first()

    return {
        "message": "Login successful",
        "user": {
            "id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": role.role_name if role else None,
            "designation": designation.designation_name if designation else None
        }
    }