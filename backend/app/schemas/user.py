from pydantic import BaseModel, EmailStr, constr

class UserCreate(BaseModel):
    name: constr(min_length=1, max_length=100)
    email: EmailStr
    password: constr(min_length=6, max_length=72)  # enforce minimal password length
    phone: constr(min_length=7, max_length=20) = None
    role: constr(max_length=20) = "user"  # default role

class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone: str | None
    role: str

    class Config:
        orm_mode = True  # allows returning SQLAlchemy models directly