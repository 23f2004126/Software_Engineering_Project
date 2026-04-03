from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime,
    DECIMAL, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.models.sale import Product  # noqa: F401 — ensures Product is registered before relationships


# =========================
# STOCK MOVEMENT MODEL (Audit Trail)
# =========================
class StockMovement(Base):
    __tablename__ = "stock_movements"

    movement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False
    )
    quantity_change = Column(Integer, nullable=False)

    movement_type = Column(String(50), nullable=False, index=True)

    previous_stock = Column(Integer, nullable=True)
    new_stock = Column(Integer, nullable=True)
    reference_id = Column(String(255), nullable=True)

    notes = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="stock_movements")
    user = relationship("User")


# =========================
# DAMAGE / LOSS RECORD MODEL
# =========================
class DamageLossRecord(Base):
    __tablename__ = "damage_loss_records"
    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False
    )

    quantity = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    estimated_loss = Column(DECIMAL(10, 2), nullable=False)

    notes = Column(Text, nullable=True)

    reported_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="damage_loss_records")
    user = relationship("User", back_populates="damage_loss_records")