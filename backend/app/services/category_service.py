"""
Service layer for categories.py routes.
Handles category CRUD operations.
"""

from sqlalchemy.orm import Session
from typing import Optional, Tuple, List

from app.models.user import Category


# =========================
# CATEGORY CRUD
# =========================

def get_category_by_id(db: Session, category_id: int) -> Optional[Category]:
    return db.query(Category).filter(Category.category_id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    return db.query(Category).filter(Category.category_name == name).first()


def get_all_categories(db: Session) -> List[Category]:
    return db.query(Category).all()


def create_category(
    db: Session,
    category_name: str
) -> Tuple[Optional[Category], Optional[str]]:
    """
    Create a new category. Rejects duplicates.
    Returns (category, None) on success, (None, error_message) on failure.
    """
    if get_category_by_name(db, category_name):
        return None, "Category already exists"

    category = Category(category_name=category_name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category, None


def update_category(
    db: Session,
    category_id: int,
    category_name: str
) -> Tuple[Optional[Category], Optional[str]]:
    """
    Rename a category. Rejects name conflicts with other categories.
    Returns (category, None) on success, (None, error_message) on failure.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return None, "Category not found"

    conflict = db.query(Category).filter(
        Category.category_name == category_name,
        Category.category_id != category_id
    ).first()
    if conflict:
        return None, "Category name already in use"

    category.category_name = category_name
    db.commit()
    db.refresh(category)
    return category, None


def delete_category(
    db: Session,
    category_id: int
) -> Tuple[bool, Optional[str]]:
    """
    Permanently delete a category.
    Returns (True, None) on success, (False, error_message) on failure.
    """
    category = get_category_by_id(db, category_id)
    if not category:
        return False, "Category not found"

    db.delete(category)
    db.commit()
    return True, None