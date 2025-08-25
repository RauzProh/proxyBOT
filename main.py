import asyncio
from core.bot import dp, bot
from db.init_db import init_models
from bot.handlers.user.commands import router 
from bot.handlers.user.menu import router_message

import pytz
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime, timedelta


from db.crud.user import get_all_users, get_user_by_id
from db.crud.proxyorders import get_proxy_orders_by_user
from db.crud.proxy import get_proxies_by_order

from templates.menu import generate_prolong

async def check_proxy():

    users = await get_all_users()
    today = datetime.today()
    for user in users:
        orders = await get_proxy_orders_by_user(user.id)
        for order in orders:
            proxies = await get_proxies_by_order(order.id)
            print(proxies)
            print(proxies[0].date_end)
            subscription_end = proxies[0].date_end
            try:
                days_left = (subscription_end - today).days
                print(days_left)
            except :
                continue
            warning_period = 1
            try:
                if days_left <=warning_period:
                    user = await get_user_by_id(order.user_id)
                    print('awdawdwa')
                    text = ''
                    text = f"Заканчивается заказ id: {order.id}!\n\n"
                    for i in proxies:
                        text+=f'Прокси: <code>{i.host}:{i.port}</code>\n'
                        text+=f'Логин: <code>{i.username}</code>\n'
                        text+=f"Пароль: <code>{i.password}</code>\n\n"

                    text+=f"Дата истечения: {i.date_end}"
                    await bot.send_message(user.tg_id, text, reply_markup=generate_prolong(order.id))
              

            except Exception as e:
                print(f"Ошибка: {e}")

async def main():
    # Создание планировщика
    scheduler = AsyncIOScheduler()

    # Настройка часового пояса для Москвы
    timezone = pytz.timezone('Etc/GMT-3')
    current_time = datetime.now(timezone)
    print(f"Текущее время в Москве: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    # await check_subscriptions()
    # Добавление задачи в планировщик с использованием CronTrigger
    scheduler.add_job(check_proxy, CronTrigger(hour=12, minute=0, timezone=timezone))
    scheduler.start()



    await init_models()
    dp.include_router(router)
    dp.include_router(router_message)
  

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())