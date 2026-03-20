from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List

from app.database import get_db
from app.models.user import User, Role, Designation
from app.core.security import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


# =========================
# SCHEMAS
# =========================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str   # this is designation name coming from frontend


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone: str

    class Config:
        from_attributes = True


# =========================
# CREATE USER (REGISTER)
# =========================
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # 1. Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Get role (default = employee)
    role = db.query(Role).filter(Role.role_name == "employee").first()
    if not role:
        raise HTTPException(status_code=500, detail="Employee role not found in DB")

    # 3. Map frontend role → designation
    designation = db.query(Designation).filter(
        Designation.designation_name == user.role
    ).first()

    if not designation:
        raise HTTPException(status_code=400, detail="Invalid designation selected")

    # 4. Hash password
    hashed_pw = hash_password(user.password)

    # 5. Create user
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pw,
        phone=user.phone,
        role_id=role.role_id,
        designation_id=designation.designation_id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# GET ALL USERS
# =========================
@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()