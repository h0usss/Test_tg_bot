import logging

from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import ADMIN_COMMAND
from src.database.dal import UserDal, ApplicationDal
from src.keyboards.keyboard import admin_command_kb, admin_command_back_kb


admin_router = Router()


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
    count_user = await UserDal.get_count_user(session=session)
    count_application = await ApplicationDal.get_count_application(session=session)

    await callback.message.edit_text(
        text=f"Статистика:\n"
             f" - Всего пользователей: {count_user}\n"
             f" - Всего заявок: {count_application}\n",
        reply_markup=admin_command_back_kb
    )
