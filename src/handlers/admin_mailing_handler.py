import asyncio
import logging
from asyncio import Semaphore

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import ADMIN_WRITE_A_TEXT
from src.database.dal import UserDal
from src.keyboards.keyboard import admin_command_back_kb, admin_command_mailing_confirm_kb, \
    admin_command_back_to_main_kb
from src.states.state import Mailing


mailing_router = Router()

@mailing_router.callback_query(F.data == "admin_mailing")
async def admin_command_mailing(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Mailing.sending_data)
    await callback.message.edit_text(
        text = ADMIN_WRITE_A_TEXT,
        reply_markup = admin_command_back_kb
    )


@mailing_router.message(Mailing.sending_data)
async def admin_command_mailing_data(message: Message, state: FSMContext):
    await state.set_state(Mailing.confirmation)

    await state.update_data(text = message.html_text)

    photo_file_id = None
    if message.photo:
        photo_file_id = message.photo[-1].file_id

    await state.update_data(photo_file_id = photo_file_id)

    await message.bot.edit_message_text(
        chat_id = message.chat.id,
        text = ADMIN_WRITE_A_TEXT,
        message_id = message.message_id - 1,
        reply_markup = None
    )
    await message.answer(
        text = "Вы уверены? Всё гуд? Точно? ",
        reply_markup = admin_command_mailing_confirm_kb
    )


@mailing_router.callback_query(F.data == "admin_send")
async def admin_command_mailing_send(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    semaphore = Semaphore(20)
    data = await state.get_data()
    all_users_ids = await UserDal.get_all_user_tg_id(session = session)

    tasks = [
        send_mailing_item(
            bot = callback.bot,
            user_id = user_id,
            text = data.get("text", ""),
            photo_file_id = data["photo_file_id"],
            semaphore = semaphore,
        )
        for user_id in all_users_ids
    ]

    results = await asyncio.gather(*tasks)

    success_count = sum(results)
    fail_count = len(all_users_ids) - success_count

    await state.clear()
    await callback.message.edit_text(
        text = f"Всё гуд!\n"
               f"✅ Успешно доставлено: {success_count}\n"
               f"❌ Не доставлено (блокировка/ошибка): {fail_count}\n",
        reply_markup = admin_command_back_to_main_kb,
    )


async def send_mailing_item(bot: Bot, user_id: int, text: str, photo_file_id: str | None, semaphore: Semaphore):
    async with semaphore:
        try:
            if photo_file_id:
                await bot.send_photo(
                    chat_id = user_id,
                    photo = photo_file_id,
                    caption = text,
                    parse_mode = "html"
                )
            else:
                await bot.send_message(
                    chat_id = user_id,
                    text = text,
                    parse_mode = "html"
                )
            return True
        except TelegramForbiddenError:
            return False
        except TelegramBadRequest as e:
            logging.error(f"Error when sending to the user with ID = {user_id}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unknown error: {e}")
            return False
        finally:
            await asyncio.sleep(0.05) # чтобы точно Telegram не ругался
