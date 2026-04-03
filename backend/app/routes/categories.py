from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.user import User, Category
from app.routes.deps import get_current_user

router = APIRouter(prefix="/api/categories", tags=["Categories"])


# =========================
# SCHEMAS
# =========================

class CategoryCreate(BaseModel):
    category_name: str


class CategoryResponse(BaseModel):
    category_id: int
    category_name: str

    class Config:
        from_attributes = True


# =========================
# POST /api/categories/
# =========================

@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Category).filter(
        Category.category_name == category.category_name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    new_category = Category(category_name=category.category_name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# =========================
# GET /api/categories/
# =========================

@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# =========================
# GET /api/categories/:category_id
# =========================

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


# =========================
# PUT /api/categories/:category_id
# =========================

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    conflict = db.query(Category).filter(
        Category.category_name == data.category_name,
        Category.category_id != category_id
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Category name already in use")

    category.category_name = data.category_name
    db.commit()
    db.refresh(category)

    return category


# =========================
# DELETE /api/categories/:category_id
# =========================

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.category_id == category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}