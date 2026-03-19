from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.models.user import User
from app.core.security import verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ✅ Request Schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ✅ Response Schema (clean output)
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True   # (Pydantic v2 fix)


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Fetch user
    user = db.query(User).filter(User.email == data.email).first()

    # ❌ Don't reveal if user exists or not (security best practice)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # ✅ Success response
    return {
        "message": "Login successful",
        "user": {
            "id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }