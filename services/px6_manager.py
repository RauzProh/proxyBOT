import asyncio
from integrations.px6 import PX6API



async def main():
    api = PX6API()
    contry = await api.get_country()
    print("Страны:", contry)
    balance = await api.get_price(20, 5, 6)
    print("Баланс:", balance)

if __name__ == "__main__":
    asyncio.run(main())
