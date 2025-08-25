from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models.proxyorders import ProxyOrder



def generate_kb_choice_country(countries: list[str]) -> InlineKeyboardMarkup:
    """
    Генерирует клавиатуру для выбора страны.
    :param countries: Список стран
    :return: InlineKeyboardMarkup
    """
    builder = InlineKeyboardBuilder()
    for country in countries:
        builder.button(text=country, callback_data=f"choosecountry_{country}")
    # builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(2)  # 2 кнопки в ряд
    return builder.as_markup()


def generate_orders(orders: list[ProxyOrder]) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()
    for order in orders:
        builder.button(text=str(order.id), callback_data=f"orderinfo_{order.id}")
    # builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(1)  # 2 кнопки в ряд
    return builder.as_markup()


def generate_prolong(id):
    builder = InlineKeyboardBuilder()
    builder.button(text="Продлить", callback_data=f"prolong_{id}")
    # builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(1)  # 2 кнопки в ряд
    return builder.as_markup()



buy_proxie = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Купить прокси", callback_data="buy"),
        ],
        # [
        #     InlineKeyboardButton(text="комментарий", callback_data="comment"),
        # ]
    ]
)

version_proxy = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="IPv6", callback_data="version_6"),
        ],
        [
            InlineKeyboardButton(text="IPv4", callback_data="version_4"),
        ],
        [
            InlineKeyboardButton(text="Pv4 Shared", callback_data="version_3"),
        ]
    ]
    
)

usermenu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мои заказы")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def check_pay_buttons(pay_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", url=pay_id[0]),
            ],
            [
                InlineKeyboardButton(text="Проверить оплату", callback_data=f"oplata_{pay_id[1]}"),
            ]
        ]
    )

def prolong_pay_buttons(pay_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", url=pay_id[0]),
            ],
            [
                InlineKeyboardButton(text="Проверить оплату", callback_data=f"prolongoplata_{pay_id[1]}"),
            ]
        ]
    )


proxy_version = {6: "IPv6", 
                 4: "IPv4",
                 3: "IPv4 Shared"}