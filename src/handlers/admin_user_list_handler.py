import math

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import USER_COUNT_IN_ONE_PAGE
from src.database.dal import UserDal
from src.database.dto import UserDto
from src.keyboards.keyboard import admin_user_list_main_kb, admin_user_list_user_kb


list_router = Router()

@list_router.callback_query(F.data.startswith("admin_users_"))
async def admin_user_list(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    page = int(callback.data.replace("admin_users_", ""))
    count_page = math.ceil(await UserDal.get_count_user(session=session) / USER_COUNT_IN_ONE_PAGE)

    users = await UserDal.get_several_users(
        page=page,
        session=session,
        return_count=USER_COUNT_IN_ONE_PAGE,
    )

    await state.update_data(list_users=users)
    await state.update_data(page=page)

    await callback.message.edit_text(
        text=f"Список пользователей:",
        reply_markup=await admin_user_list_main_kb(
            users=users,
            page=page,
            count_page=count_page
        )
    )


@list_router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_list_user(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.replace("admin_user_", ""))
    data = await state.get_data()
    selected_user = UserDto

    for user in data["list_users"]:
        if user.id == user_id:
            selected_user = user
            break

    await callback.message.edit_text(
        text=f"Данные пользователя id = {selected_user.id}: \n"
             f" - Телеграм ID: {selected_user.tg_id}\n"
             f" - ФИО: {selected_user.fio}\n"
             f" - Номер телефона: {selected_user.phone_number}\n"
             f" - Админ: {selected_user.is_admin}\n"
             f" - День рождения: {selected_user.birthday.date()}\n"
             f" - Зарегистрирован: {selected_user.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n",
        reply_markup=await admin_user_list_user_kb(last_visit_page=data["page"])
    )


@list_router.callback_query(F.data == "ignore")
async def ignore(callback: CallbackQuery):
    pass
