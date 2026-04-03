from pydantic import BaseModel, EmailStr
from typing import Optional


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: str = "employee"           # maps to Designation.designation_name in the route


class UserResponse(BaseModel):
    user_id: int                     # model PK: user_id (not id)
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: Optional[str] = None       # resolved from Role.role_name
    designation: Optional[str] = None  # resolved from Designation.designation_name

    class Config:
        from_attributes = True       # Pydantic v2


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse