import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext



from db.crud.user import get_user_by_tg_id, get_admins
from db.crud.proxyorders import get_proxy_orders_by_user, create_proxy_order, get_proxy_order_by_id
from db.crud.proxy import create_proxy, get_proxies_by_order

from integrations.px6 import PX6API

from templates.menu import version_proxy, generate_orders

from templates.menu import generate_kb_choice_country, check_pay_buttons, proxy_version, generate_prolong, prolong_pay_buttons, usermenu
from integrations.yookassa import get_payment_link, check_oplata
from aiogram import Router

# Создаем Router
router_message = Router()







@router_message.callback_query(lambda c: c.data == "buy")
async def buy_proxy(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await callback_query.message.answer("Выберите версию прокси:", reply_markup=version_proxy)


# @router_message.callback_query(lambda c: c.data == "buy")
# async def buy_proxy(callback_query: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     country = data.get("chosen_country")
#     if not country:
#         await callback_query.message.answer("Пожалуйста, сначала выберите страну.")
#         await callback_query.answer()
#         return
#     await callback_query.message.answer(f"Покупка прокси для страны: {country}")
#     # Здесь можно добавить логику покупки прокси
#     await callback_query.answer()


@router_message.callback_query(lambda c: c.data.startswith("version_"))
async def choose_version(callback_query: types.CallbackQuery, state: FSMContext):
    
    await callback_query.bot.answer_callback_query(callback_query.id)
    version = callback_query.data.split("_")[1]
    print(version)
    await state.update_data(chosen_version=version)
    pxAPI = PX6API()
    countries = await pxAPI.get_country(version)
    data = await state.get_data()
    if data.get("b_count"):
        data.pop("b_count", None)
    if data.get('period'):
        data.pop('period', None)
    # price = await pxAPI.get_price(1,1,version)
    # await callback_query.message.answer(f'1 шт на 1д стоит: {price['price_single']}')
    await callback_query.message.answer(f"Выберите страну:", reply_markup=generate_kb_choice_country(countries['list']))

@router_message.callback_query(lambda c: c.data.startswith("choosecountry_"))
async def choose_country(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    await callback_query.bot.answer_callback_query(callback_query.id)
    country = callback_query.data.split("_")[1]
    await state.update_data(chosen_country=country)
    await callback_query.message.answer(f"Вы выбрали страну: {country}")
    data = await state.get_data()
    version = data['chosen_version']
    pxAPI = PX6API()
    getcount = await pxAPI.get_count(country, version)
    await state.update_data(count=getcount['count'])
    if data.get("b_count"):
        data.pop("b_count", None)
    if data.get('period'):
        data.pop('period', None)
    print("вывод в фиат")
    print(getcount)
    await callback_query.message.answer(f"в наличии: {getcount['count']}")
    await callback_query.message.answer(f'Напишите нужное вам количество')


@router_message.message()
async def messages(message: types.Message, state: FSMContext):
    if message.text == "Мои заказы":
        user = await get_user_by_tg_id(message.from_user.id)
        orders = await get_proxy_orders_by_user(user.id)

        if not orders:
            await message.answer("У вас пока нет заказов.")
            return

        # Преобразуем каждый заказ в строку
        orders_text = "\n\n".join(
            f"Заказ №{order.id}\nСтрана: {order.country}\nВерсия: {proxy_version[order.version]}"
            for order in orders
        )

        await message.answer(orders_text, reply_markup=generate_orders(orders))

    data = await state.get_data()
    if data.get("prolong_id"):
        try:
            print('пошла')
            print(data["prolong_id"])
            prolong_period = int(message.text)
            await state.update_data(prolong_period = prolong_period)
            proxies_order = await get_proxy_order_by_id(data['prolong_id'])
            if data['chosen_version'] == "6" and prolong_period<3:
                    await message.answer('Можно продлить от 3 дней, отправьте другое количество')
                    return
            if data['chosen_version'] in ["3", 4] and prolong_period<7:
                await message.answer('Можно продлить от 7 дней, отправьте другое количество')
                return

            proxies = await get_proxies_by_order(data['prolong_id'])
            spisok_prolong_id = []
            for i in proxies:
                spisok_prolong_id.append(i.px6_id)
            
            pxAPI = PX6API()
            print(proxies_order)
            get_price = await pxAPI.get_price(len(proxies), prolong_period )
            pay_link = get_payment_link(get_price['price'], "example@mail.ru")
            await state.update_data(paym_id = pay_link[1])
            await message.answer(f"Продлить на 5 дней стоит: {get_price['price']}", reply_markup=prolong_pay_buttons(pay_link))

            

            
        except Exception as e:
            print(f"Ошибка: {e}")
    if data.get("chosen_version") and data.get('chosen_country') and data.get('count'):
        print('dawd')
        
        if not data.get("b_count"):
            print('dawd')
            try:
                b_count = int(message.text)
                print('go')
                await state.update_data(b_count=b_count)
                await message.answer('Напишите период в днях')
            except ValueError:
                await message.answer('Пожалуйста, введите число!')
            return  # останавливаем дальнейшую обработку
        
        if not data.get('period'):
            try:
                period = int(message.text)
                print(data['chosen_version'])
                if data['chosen_version'] == "6" and period<3:
                    await message.answer('Можно купить от 3 дней, отправьте другое количество')
                    return
                if data['chosen_version'] in ["3", "4"] and period<7:
                    await message.answer('Можно купить от 7 дней, отправьте другое количество')
                    return

                await state.update_data(period=period)
                
                data = await state.get_data()  # обновляем данные
                pxAPI = PX6API()
                final_price = await pxAPI.get_price(data['b_count'], period, data["chosen_version"])
                await state.update_data(final_price=final_price)
                
                link = get_payment_link(final_price['price'], "example@mail.ru")
                await state.update_data(paym_id = pay_link[1])


                await message.answer(f'Финальная цена: {final_price['price']}',reply_markup=check_pay_buttons(link))
            except ValueError:
                await message.answer('Пожалуйста, введите число!')



@router_message.callback_query(lambda c: c.data.startswith("orderinfo_" ))
async def orderinfo(call: types.CallbackQuery, state: FSMContext):
    await call.bot.answer_callback_query(call.id)
    order_db_id =  call.data.split("orderinfo_")[1]
    proxies = await get_proxies_by_order(order_db_id)
    print('awdawdwa')
    text = ''
    text = f"Заказ id: {order_db_id}\n\n"
    for i in proxies:
        text+=f'Прокси: <code>{i.host}:{i.port}</code>\n'
        text+=f'Логин: <code>{i.username}</code>\n'
        text+=f"Пароль: <code>{i.password}</code>\n\n"

    text+=f"Дата истечения: {i.date_end}"
    await call.message.answer(text, reply_markup=generate_prolong(order_db_id))


@router_message.callback_query(lambda c: c.data.startswith("oplata_" ))
async def get_oplata(call: types.CallbackQuery, state: FSMContext):
    await call.bot.answer_callback_query(call.id)
    print(call.data)
    pay_id =  call.data.split("oplata_")[1]

    res = check_oplata(pay_id)
    if res == "pending":
        await call.message.answer("Вы ещё не оплатили!")
    elif res == "succeeded":
        await call.message.answer("Оплата прошла успешно", reply_markup=usermenu)
    pxAPI = PX6API()
    data = await state.get_data()
    if data["pay_id"]:
        paym_id = data["pay_id"]
    else:
        return
    buy = await pxAPI.buy(data['b_count'], data['period'], data['chosen_country'], data['chosen_version'] 
    )
    await state.clear()

    # buy = {'status': 'yes', 'user_id': '491758', 'balance': '310.48', 'currency': 'RUB', 'date_mod': '2024-11-03 02:13:10', 'order_id': 12740532, 'count': '10', 'price': '36.00', 'period': '5', 'version': '6', 'type': 'http', 'country': 'au', 'list': {'34073930': {'id': '34073930', 'version': '6', 'ip': '2001:19f0:5801:c24:7bc8:3c57:fa87:ffba', 'host': '149.28.161.95', 'port': '12013', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073931': {'id': '34073931', 'version': '6', 'ip': '2001:19f0:5801:c24:6427:a4f7:c94a:27af', 'host': '149.28.161.95', 'port': '12016', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073932': {'id': '34073932', 'version': '6', 'ip': '2001:19f0:5801:c24:cd05:5227:71a0:9c09', 'host': '149.28.161.95', 'port': '12017', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073933': {'id': '34073933', 'version': '6', 'ip': '2001:19f0:5801:c24:c32a:9029:ecb5:cc7f', 'host': '149.28.161.95', 'port': '12018', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073934': {'id': '34073934', 'version': '6', 'ip': '2001:19f0:5801:c24:e19c:cae1:ffbe:2c0d', 'host': '149.28.161.95', 'port': '12020', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073935': {'id': '34073935', 'version': '6', 'ip': '2001:19f0:5801:c24:2e2d:4a48:1554:985e', 'host': '149.28.161.95', 'port': '12022', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073936': {'id': '34073936', 'version': '6', 'ip': '2001:19f0:5801:c24:27f2:771e:b3a7:e7d9', 'host': '149.28.161.95', 'port': '12034', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073937': {'id': '34073937', 'version': '6', 'ip': '2001:19f0:5801:c24:bf3a:f950:fde3:d1d4', 'host': '149.28.161.95', 'port': '12046', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073938': {'id': '34073938', 'version': '6', 'ip': '2001:19f0:5801:c24:fe2c:a277:9730:a207', 'host': '149.28.161.95', 'port': '12047', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}, '34073939': {'id': '34073939', 'version': '6', 'ip': '2001:19f0:5801:c24:468a:5b11:b575:a1fc', 'host': '149.28.161.95', 'port': '12050', 'user': 'ass6Ge', 'pass': 'wza9Ga', 'type': 'http', 'date': '2025-08-25 00:02:55', 'date_end': '2025-08-30 00:02:55', 'unixtime': 1756069375, 'unixtime_end': 1756501375, 'active': '1'}}}
    user = await get_user_by_tg_id(call.from_user.id)
    order = await create_proxy_order(user_id=user.id,order_id_px6=buy['order_id'], count=buy['count'], price=buy['price'], period=buy['period'], version=buy['version'], country=buy['country'])
    for proxy in buy['list'].values():   # теперь proxy = {...}
        await create_proxy(
            order_id=order.id,
            px6_id=int(proxy['id']),
            country=buy['country'],
            host=proxy['host'],
            port=proxy['port'],
            username=proxy['user'],   # у тебя в JSON ключ называется "user", а не "username"
            password=proxy['pass'],   # и "pass", а не "password"
            date_start=proxy['date'],
            date_end=proxy['date_end']
        )   

    admins = await get_admins()

    tg_id = call.from_user.id
    proxies = await get_proxies_by_order(order.id)
    print('awdawdwa')
    text = ''
    text = f"Заказ id: {order.id}\n\n"
    for i in proxies:
        text+=f'Прокси: <code>{i.host}:{i.port}</code>\n'
        text+=f'Логин: <code>{i.username}</code>\n'
        text+=f"Пароль: <code>{i.password}</code>\n\n"

    text+=f"Дата истечения: {i.date_end}"
    await call.message.answer(text, reply_markup=generate_prolong(order.id))
        

    tasks = []
    for admin in admins:
        tasks.append(call.bot.send_message(admin.tg_id, f"Пользователь <code>{tg_id}</code> купил #{order.id} {order.version} {order.count}шт за {order.price}"))
    await asyncio.gather(*tasks, return_exceptions=True)



@router_message.callback_query(lambda c: c.data.startswith("prolong_" ))
async def prolong(call: types.CallbackQuery, state: FSMContext):
    await call.bot.answer_callback_query(call.id)
    prolong =  call.data.split("prolong_")[1]

    await call.message.answer("Напишите на сколько дней продлить")
    await state.update_data(prolong_id=prolong)


@router_message.callback_query(lambda c: c.data.startswith("prolongoplata_" ))
async def get_prolongoplata(call: types.CallbackQuery, state: FSMContext):
    await call.bot.answer_callback_query(call.id)
    print(call.data)
    pay_id =  call.data.split("prolongoplata_")[1]

    res = check_oplata(pay_id)
    data = await state.get_data()
    if data["pay_id"]:
        paym_id = data["pay_id"]
    else:
        return
    prolong_period = data['prolong_period']
    prolong_id = data['prolong_id']
    if res == "pending":
        await call.message.answer("Вы ещё не оплатили!")
    elif res == "succeeded":
        pass
    await state.clear()
    proxies = await get_proxies_by_order(prolong_id)
    spisok_prolong_id = []
    for i in proxies:
        spisok_prolong_id.append(i.px6_id)
    await call.message.answer("Оплата прошла успешно")
    pxAPI = PX6API()
    res = await pxAPI.prolong(spisok_prolong_id,prolong_period)
    print(res)
    order = await get_proxy_order_by_id(prolong_id)

    admins = await get_admins()

    tg_id = call.from_user.id

    tasks = []
    for admin in admins:
        tasks.append(call.bot.send_message(admin.tg_id, f"Пользователь <code>{tg_id}</code> продлил #{order.id} {order.version} {order.count}шт за {order.price}"))
    await asyncio.gather(*tasks, return_exceptions=True)

    if res:
        data.pop("prolong_id", None)
        data.pop("prolong_period", None)
