import logging

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import ADMIN_COMMAND
from src.database.dao import UserDao, ApplicationDao
from src.keyboards.keyboard import admin_command_kb, admin_command_back_kb

admin_router = Router()


async def send_application_all_admins(session: AsyncSession, bot: Bot, application_id: int):
    admin_ids = await UserDao.get_all_admins(session)
    application = await ApplicationDao.get_application(session, application_id)
    user = await UserDao.get_user(
        session=session,
        user_id=application.user_id
    )

    text = (f"Заявка №{application.id}\n"
            f" - Фио: {user.fio}\n"
            f" - Телефон: {user.phone_number}\n"
            f" - Пол: {application.gender.name}\n"
            f" - Любовный интерес: {application.love.name}\n"
            f" - Машинки: {application.car}\n")

    for admin_id in admin_ids:
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=application.cat_photo_id,
                caption=text
            )
        except Exception as e:
            logging.error(f"Error send message for user {admin_id}: {e}")
            logging.error(f"Error send message for user {admin_id}: {e}")


@admin_router.message(Command("admin"))
async def admin_command_new(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    await message.answer(
        text=ADMIN_COMMAND,
        reply_markup=admin_command_kb
    )


@admin_router.callback_query(F.data == "admin_back")
async def admin_command_edit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text=ADMIN_COMMAND,
        reply_markup=admin_command_kb
    )


@admin_router.callback_query(F.data == "admin_statistics")
async def admin_command_statistics(callback: CallbackQuery, session: AsyncSession):
    count_user = await UserDao.get_count_user(session=session)
    count_application = await ApplicationDao.get_count_application(session=session)

    await callback.message.edit_text(
        text=f"Статистика:\n"
             f" - Всего пользователей: {count_user}\n"
             f" - Всего заявок: {count_application}\n",
        reply_markup=admin_command_back_kb
    )
