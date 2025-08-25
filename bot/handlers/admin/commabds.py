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

router_admin = Router()

@router_admin.message(Command("admin"))
async def admin_command(message: types.Message):
    tg_id = message.from_user.id
    user = await get_user_by_tg_id(tg_id)
    if user and user.role == Role.ADMIN:
        await message.answer("Вы уже администратор.")
        