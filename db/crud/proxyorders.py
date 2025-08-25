# crud_proxyorder.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from db.models.proxyorders import ProxyOrder, ProxyOrderStatus


from db.session import SessionLocal


# ✅ Создание заказа
async def create_proxy_order(
    user_id: int,
    count: int,
    period: int,
    country: str,
    price: float,
    version: int = 6,
    type_: str = "http",
    auto_prolong: bool = False,
    status: str = ProxyOrderStatus.pending.value,
    order_id_px6: int | None = None,
) -> ProxyOrder:
    order = ProxyOrder(
        user_id=user_id,
        count=count,
        period=period,
        country=country,
        version=version,
        type=type_,
        price=price,
        auto_prolong=auto_prolong,
        status=status,
        order_id_px6=order_id_px6,
    )
    async with SessionLocal() as session:
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


# ✅ Получение заказа по id
async def get_proxy_order_by_id( order_id: int) -> ProxyOrder | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(ProxyOrder).where(ProxyOrder.id == order_id)
        )
        return result.scalar_one_or_none()


# ✅ Получение всех заказов пользователя
async def get_proxy_orders_by_user(user_id: int) -> list[ProxyOrder]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(ProxyOrder).where(ProxyOrder.user_id == user_id)
        )
        return result.scalars().all()


# ✅ Обновление заказа
async def update_proxy_order(order_id: int, **kwargs) -> ProxyOrder | None:
    async with SessionLocal() as session:
        await session.execute(
            update(ProxyOrder)
            .where(ProxyOrder.id == order_id)
            .values(**kwargs)
        )
        await session.commit()

        result = await session.execute(
            select(ProxyOrder).where(ProxyOrder.id == order_id)
        )
        return result.scalar_one_or_none()


# ✅ Удаление заказа
async def delete_proxy_order(order_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            delete(ProxyOrder).where(ProxyOrder.id == order_id)
        )
        await session.commit()
        return result.rowcount > 0
