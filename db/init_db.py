import asyncio
from db.session import engine
from db.base import Base
from db.models.user import User
from db.models.proxyorders import ProxyOrder
from db.models.proxy import Proxy







async def init_models():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("All tables created.")
        await conn.commit()

if __name__ == "__main__":
    asyncio.run(init_models())  