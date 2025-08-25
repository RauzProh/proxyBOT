from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base


class Proxy(Base):
    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("proxyorders.id"), nullable=False)  # <- добавили ForeignKey
    px6_id: Mapped[int] = mapped_column(Integer, nullable=False)
    host: Mapped[str] = mapped_column(String(50), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="http")
    country: Mapped[str] = mapped_column(String(20), nullable=False)
    date_start: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    date_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Связь с заказом
    order: Mapped["ProxyOrder"] = relationship("ProxyOrder", back_populates="proxies")