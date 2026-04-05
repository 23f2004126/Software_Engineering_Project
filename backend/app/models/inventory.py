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
    # schema.sql uses `quantity` for the moved amount
    quantity_change = Column(Integer, nullable=False, name="quantity")

    movement_type = Column(String(50), nullable=False, index=True)
    # schema.sql uses `reason` for additional details
    notes = Column(Text, nullable=True, name="reason")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product")


# =========================
# DAMAGE / LOSS RECORD MODEL
# =========================
class DamageLossRecord(Base):
    __tablename__ = "damage_loss_records"
    # schema.sql uses `record_id` as the primary key
    id = Column(Integer, primary_key=True, index=True, name="record_id")

    product_id = Column(
        Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False
    )

    # schema.sql uses `quantity_lost`
    quantity = Column(Integer, nullable=False, name="quantity_lost")
    # schema.sql uses `loss_type` (damaged/expired/theft/other) for this field
    reason = Column(String(20), nullable=False, name="loss_type")
    # schema.sql uses `loss_value` for the estimated monetary loss
    estimated_loss = Column(DECIMAL(10, 2), nullable=True, name="loss_value")

    # schema.sql uses `reason` text column for notes/details
    notes = Column(Text, nullable=True, name="reason")

    reported_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    product = relationship("Product")
    user = relationship("User", back_populates="damage_loss_records")