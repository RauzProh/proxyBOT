from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram import Router
from integrations.px6 import PX6API
from templates.menu import generate_kb_choice_country, buy_proxie
from aiogram.types import FSInputFile 


from db.models.user import Role, User
# from db.crud.user import get_user_by_tg_id, create_user
from db.crud.user import get_user_by_tg_id, create_user, update_user




photo = FSInputFile("proxy.png")  # путь к файлу
router = Router()

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id

    
    # Проверяем, есть ли уже пользователь
    user = await get_user_by_tg_id(tg_id)
    print(user)
    if user == None:
        # Создаём нового пользователя с минимальными данными
        
        user = await create_user(
            tg_id=tg_id,
        )
        print(tg_id)
        if str(tg_id) in ['794637958', "5877487979"]:
            print('Делаем')
            await update_user(tg_id, role = Role.ADMIN)
    await message.answer_photo(photo=photo, caption=f"Добро пожаловать, {message.from_user.full_name}!", reply_markup=buy_proxie)
    # await message.answer(f"Добро пожаловать, {message.from_user.full_name}!", reply_markup=buy_proxie)
    # pxAPI = PX6API()
    # countries = await pxAPI.get_country()
    # print(countries['list'])
    # await message.answer(f"Доступные страны для прокси:", reply_markup=generate_kb_choice_country(countries['list']))

@router.message(Command("menu"))
async def admin_command(message: types.Message):
    tg_id = message.from_user.id
    user = await get_user_by_tg_id(tg_id)
    if user and user.role == Role.ADMIN:
        await message.answer("Вы уже администратор.")
        