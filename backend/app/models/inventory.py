from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Date,
    DECIMAL, Enum, Text, Boolean, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.models.sale import Product


# =========================
# STOCK MOVEMENT MODEL (Audit Trail)
# =========================
class StockMovement(Base):
    __tablename__ = "stock_movements"

    movement_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)

    movement_type = Column(
        Enum(
            "purchase", "sale", "damage", "loss", "return", "adjustment",
            name="movement_type"
        ),
        nullable=False,
        index=True
    )

    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    new_stock = Column(Integer, nullable=False)

    reference_id = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="stock_movements")
    user = relationship("User")

# =========================
# DAMAGE/LOSS RECORD MODEL
# =========================
class DamageLossRecord(Base):
    __tablename__ = "damage_loss_records"

    record_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)

    quantity = Column(Integer, nullable=False)
    reason = Column(
        Enum(
            "expired", "damaged", "loss", "theft", "other",
            name="loss_reason"
        ),
        nullable=False,
        index=True
    )

    cost = Column(DECIMAL(10, 2), nullable=False)
    notes = Column(Text, nullable=True)

    reported_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product", back_populates="damage_loss_records")
    user = relationship("User", back_populates="damage_loss_records")
