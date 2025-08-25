import uuid
from yookassa import Configuration, Payment
from config import YK_account_id, YK_secret_key

Configuration.account_id = YK_account_id
Configuration.secret_key = YK_secret_key

def get_payment_link(summ, email):
    payment = Payment.create({
            "amount": {
                "value": f"{summ}",  # Сумма оплаты
                "currency": "RUB"    # Валюта
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/Bl1tzBl1tz_Bot"  # URL возврата после оплаты
            },
            "capture": False,
            "description": "Оплата подписки",
            "receipt": {
                "customer": {
                    "email": email
                },
                "items": [
                    {
                        "description": f"Прокси",  # Указываем тариф в описании товара
                        "quantity": 1,  # Количество
                        "amount": {
                            "value": f"{summ}",  # Стоимость товара
                            "currency": "RUB"  # Валюта
                        },
                        "vat_code": 1,  # Код НДС
                    }
                ]
            }
        })

        # Получаем ссылку для оплаты
    confirmation_url = payment.confirmation.confirmation_url
    pay_id = payment.id
    return [confirmation_url,pay_id]


# print(get_payment_link("1.97",'example@mail.ru'))

def check_oplata(pay_id):
    payment = Payment.find_one(pay_id)
    return payment.status