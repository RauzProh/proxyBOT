# crud_proxy.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from db.models.proxy import Proxy
from db.session import SessionLocal
from datetime import datetime



# ✅ Создание прокси
async def create_proxy(
    order_id: int,
    px6_id: int,
    host: str,
    port: str,
    country: str,
    username: str | None = None,
    password: str | None = None,
    type_: str = "http",
    date_start: datetime | None = None,
    date_end: datetime | None = None,
    active: bool = True,
) -> Proxy:
    proxy = Proxy(
        order_id=order_id,
        px6_id=px6_id,
        host=host,
        port=port,
        username=username,
        password=password,
        type=type_,
        country=country,
        date_start=date_start or datetime.utcnow(),
        date_end=date_end,
        active=active,
    )
    async with SessionLocal() as session:
        session.add(proxy)
        await session.commit()
        await session.refresh(proxy)
        return proxy


# ✅ Получение прокси по id
async def get_proxy_by_id(proxy_id: int) -> Proxy | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Proxy).where(Proxy.id == proxy_id)
        )
        return result.scalar_one_or_none()


# ✅ Получение всех прокси по order_id
async def get_proxies_by_order(order_id: int) -> list[Proxy]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Proxy).where(Proxy.order_id == order_id)
        )
        return result.scalars().all()


# ✅ Обновление прокси
async def update_proxy(proxy_id: int, **kwargs) -> Proxy | None:
    async with SessionLocal() as session:
        await session.execute(
            update(Proxy)
            .where(Proxy.id == proxy_id)
            .values(**kwargs)
        )
        await session.commit()

    return await get_proxy_by_id(proxy_id)


# ✅ Удаление прокси
async def delete_proxy(proxy_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            delete(Proxy).where(Proxy.id == proxy_id)
        )
        await session.commit()
        return result.rowcount > 0
