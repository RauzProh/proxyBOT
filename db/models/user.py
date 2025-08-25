from datetime import datetime
from typing import List

from sqlalchemy import String, Integer, Float, DateTime, Enum, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base
import enum

class Role(enum.Enum):
    UNREGISTERED = "unregistered"
    CLIENT = 'client'
    ADMIN = "admin"



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.UNREGISTERED)
    tg_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Связь с заказами
    orders: Mapped[List["ProxyOrder"]] = relationship(back_populates="user")
