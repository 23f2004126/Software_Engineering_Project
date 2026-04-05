"""
Service layer for user.py and auth.py routes.
Handles user CRUD, registration, and login verification.
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple, List

from app.models.user import User, Role, Designation
from app.core.security import hash_password, verify_password


# =========================
# HELPERS
# =========================

def _get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.role_id == role_id).first()


def _get_designation(db: Session, designation_id: int) -> Optional[Designation]:
    return db.query(Designation).filter(
        Designation.designation_id == designation_id
    ).first()


def _build_user_dict(user: User, role: Optional[Role], designation: Optional[Designation]) -> dict:
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": role.role_name if role else None,
        "designation": designation.designation_name if designation else None,
    }


# =========================
# AUTH
# =========================

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> Tuple[Optional[User], Optional[str]]:
    """
    Verify email + password.
    Returns (user, None) on success, (None, error_message) on failure.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None, "Invalid email or password"
    if not verify_password(password, user.password):
        return None, "Invalid email or password"
    return user, None


def get_user_with_role(db: Session, user: User) -> dict:
    """Return a full user dict with role and designation names resolved."""
    role = _get_role(db, user.role_id)
    designation = _get_designation(db, user.designation_id) if user.designation_id else None
    return _build_user_dict(user, role, designation)


# =========================
# USER CRUD
# =========================

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    return db.query(User).filter(User.phone == phone).first()


def get_all_users(db: Session) -> List[dict]:
    """Return all users with their role and designation names resolved."""
    users = db.query(User).all()
    result = []
    for u in users:
        role = _get_role(db, u.role_id)
        designation = _get_designation(db, u.designation_id) if u.designation_id else None
        result.append(_build_user_dict(u, role, designation))
    return result


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    phone: str,
    designation_name: str
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Register a new user. Role is always 'employee' by default.
    Returns (user_dict, None) on success, (None, error_message) on failure.
    """
    if get_user_by_email(db, email):
        return None, "Email already registered"
    if get_user_by_phone(db, phone):
        return None, "Phone number already registered"

    role = db.query(Role).filter(Role.role_name == "employee").first()
    if not role:
        return None, "Default employee role not found in DB"

    designation = db.query(Designation).filter(
        Designation.designation_name == designation_name
    ).first()
    if not designation:
        return None, f"Invalid designation: '{designation_name}'"

    new_user = User(
        name=name,
        email=email,
        password=hash_password(password),
        phone=phone,
        role_id=role.role_id,
        designation_id=designation.designation_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return _build_user_dict(new_user, role, designation), None


def update_user(
    db: Session,
    user_id: int,
    name: str,
    email: str,
    password: str,
    phone: str,
    designation_name: str
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Update an existing user's details.
    Returns (user_dict, None) on success, (None, error_message) on failure.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None, "User not found"

    conflict = db.query(User).filter(
        User.email == email, User.user_id != user_id
    ).first()
    if conflict:
        return None, "Email already in use"

    designation = db.query(Designation).filter(
        Designation.designation_name == designation_name
    ).first()
    if not designation:
        return None, "Invalid designation"

    user.name = name
    user.email = email
    user.phone = phone
    user.password = hash_password(password)
    user.designation_id = designation.designation_id

    db.commit()
    db.refresh(user)

    role = _get_role(db, user.role_id)
    return _build_user_dict(user, role, designation), None


def delete_user(
    db: Session,
    user_id: int,
    current_user_id: int
) -> Tuple[bool, Optional[str]]:
    """
    Permanently delete a user. Cannot delete yourself.
    Returns (True, None) on success, (False, error_message) on failure.
    """
    if user_id == current_user_id:
        return False, "You cannot delete your own account"

    user = get_user_by_id(db, user_id)
    if not user:
        return False, "User not found"

    db.delete(user)
    db.commit()
    return True, None