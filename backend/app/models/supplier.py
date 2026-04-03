from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Date,
    DECIMAL, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


# =========================
# SUPPLIER PAYMENT
# =========================
class SupplierPayment(Base):
    __tablename__ = "supplier_payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(
        Integer, ForeignKey("suppliers.supplier_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    amount = Column(DECIMAL(10, 2), nullable=False)
    mode = Column(String(20), nullable=False)   # cash / cheque / transfer / upi

    po_id = Column(Integer, ForeignKey("purchase_orders.po_id"), nullable=True)
    cheque_no = Column(String(50), nullable=True)

    status = Column(String(20), default="pending", nullable=False, index=True)  # pending / paid

    due_date = Column(Date, nullable=True)
    paid_date = Column(Date, nullable=True)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    supplier = relationship("Supplier", back_populates="payments")