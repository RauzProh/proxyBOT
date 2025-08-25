from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
from typing import List


class ProxyOrderStatus(PyEnum):
    pending = "pending"
    paid = "paid"
    active = "active"


class ProxyOrder(Base):
    __tablename__ = "proxyorders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    count: Mapped[int] = mapped_column(nullable=False)
    period: Mapped[int] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    version: Mapped[int] = mapped_column(default=6)
    type: Mapped[str] = mapped_column(String(10), default="http")
    price: Mapped[float] = mapped_column(nullable=False)
    auto_prolong: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    order_id_px6: Mapped[int] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    proxies: Mapped[List["Proxy"]] = relationship("Proxy", back_populates="order")