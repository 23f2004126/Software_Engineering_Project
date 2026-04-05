from pydantic import BaseModel, EmailStr
from typing import Optional


# =========================
# AUTH SCHEMAS
# =========================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginUserResponse(BaseModel):
    id: int                          # maps to user.user_id (returned as 'id' in auth response)
    name: str
    email: EmailStr
    role: Optional[str] = None
    designation: Optional[str] = None

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str
    user: LoginUserResponse