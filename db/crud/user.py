from sqlalchemy import select
from db.session import SessionLocal
from db.models.user import User, Role
from db.models.proxyorders import ProxyOrder    
from db.models.proxy import Proxy




async def get_all_users() -> list[User]:
    async with SessionLocal() as session:
        res = await session.execute(select(User))
        return res.scalars().all()


# Получить пользователя по ID
async def get_user_by_id(user_id: int) -> User | None:
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.id == user_id))
        return res.scalar_one_or_none()
    



# Получить пользователя по Telegram ID
async def get_user_by_tg_id(tg_id: str) -> User | None:
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.tg_id == tg_id))
        return res.scalar_one_or_none()

# Создать нового пользователя
async def create_user(tg_id: str, username: str | None = None) -> User:
    async with SessionLocal() as session:
        async with session.begin():
            user = User(tg_id=tg_id, username=username)
            session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
async def update_user(tg_id: int, **kwargs) -> User | None:
    async with SessionLocal() as session:
        async with session.begin():
            res = await session.execute(select(User).where(User.tg_id == tg_id))
            user = res.scalar_one_or_none()
            if not user:
                return None
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user



# Обновить баланс пользователя
async def update_balance(tg_id: str, amount: float) -> User | None:
    async with SessionLocal() as session:
        async with session.begin():
            res = await session.execute(select(User).where(User.tg_id == tg_id))
            user = res.scalar_one_or_none()
            if not user:
                return None
            user.balance += amount
            session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# Проверка существования пользователя
async def user_exists(tg_id: str) -> bool:
    user = await get_user_by_tg_id(tg_id)
    return user is not None


async def get_admins():
    async with SessionLocal() as session:
        res = await session.execute(select(User).where(User.role == Role.ADMIN))
        return res.scalars().all()
    


