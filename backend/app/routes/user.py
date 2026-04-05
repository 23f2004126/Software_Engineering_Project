from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
import re

from app.database import get_db
from app.models.user import User, Role, Designation
from app.core.security import hash_password
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


# =========================
# SCHEMAS
# =========================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str                           # maps to designation_name

    @validator("phone")
    def validate_phone(cls, v):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("Phone number must be exactly 10 digits")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone: str
    role: Optional[str] = None
    designation: Optional[str] = None

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse


# =========================
# POST /api/users/register
# =========================

@router.post("/register", response_model=RegisterResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    role = db.query(Role).filter(Role.role_name == "employee").first()
    if not role:
        raise HTTPException(status_code=500, detail="Default employee role not found in DB")

    designation = db.query(Designation).filter(
        Designation.designation_name == user.role
    ).first()
    if not designation:
        raise HTTPException(status_code=400, detail=f"Invalid designation: '{user.role}'")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone=user.phone,
        role_id=role.role_id,
        designation_id=designation.designation_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful",
        "user": {
            "user_id": new_user.user_id,
            "name": new_user.name,
            "email": new_user.email,
            "phone": new_user.phone,
            "role": role.role_name,
            "designation": designation.designation_name
        }
    }


# =========================
# GET /api/users/
# =========================

@router.get("/", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users = db.query(User).all()
    result = []

    for u in users:
        role = db.query(Role).filter(Role.role_id == u.role_id).first()
        desig = None
        if u.designation_id:
            d = db.query(Designation).filter(
                Designation.designation_id == u.designation_id
            ).first()
            desig = d.designation_name if d else None

        result.append(UserResponse(
            user_id=u.user_id,
            name=u.name,
            email=u.email,
            phone=u.phone,
            role=role.role_name if role else None,
            designation=desig
        ))

    return result


# =========================
# GET /api/users/:user_id
# =========================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    desig = None
    if user.designation_id:
        d = db.query(Designation).filter(
            Designation.designation_id == user.designation_id
        ).first()
        desig = d.designation_name if d else None

    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=role.role_name if role else None,
        designation=desig
    )


# =========================
# PUT /api/users/:user_id
# =========================

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    conflict = db.query(User).filter(
        User.email == data.email, User.user_id != user_id
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Email already in use")

    designation = db.query(Designation).filter(
        Designation.designation_name == data.role
    ).first()
    if not designation:
        raise HTTPException(status_code=400, detail="Invalid designation")

    user.name = data.name
    user.email = data.email
    user.phone = data.phone
    user.password = hash_password(data.password)
    user.designation_id = designation.designation_id

    db.commit()
    db.refresh(user)

    role = db.query(Role).filter(Role.role_id == user.role_id).first()

    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=role.role_name if role else None,
        designation=designation.designation_name
    )


# =========================
# DELETE /api/users/:user_id
# =========================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}