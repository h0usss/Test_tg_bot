import asyncio

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.chat_action import ChatActionSender
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import CONTACTS
from src.database.dao import UserDao
from src.handlers.user_application_handler import application_start
from src.keyboards.keyboard import main_menu_kb, contacts_kb
from src.states.state import Register, Application


user_router = Router()

@user_router.message(CommandStart())
async def main_menu(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()

    user = await UserDao.get_user(
        session=session,
        tg_id=message.from_user.id
    )

    if user:
        await message.answer(text="Выбирай что делать дальше🥰",
                             reply_markup=main_menu_kb)
    else:
        await state.set_state(Register.fio)
        await message.answer(text="Дратути, прежде чем получить фулл нужно зарегистрироваться💋\n\nВведите своё ФИО:",
                             reply_markup=ReplyKeyboardRemove())


@user_router.message(F.text == "Оставить заявку📝")
async def main_menu_application(message: Message, state: FSMContext):
    await state.set_state(Application.start)
    await application_start(message=message, state=state)


@user_router.message(F.text == "Контакты")
async def main_menu_contacts(message: Message):
    await message.answer(text=CONTACTS,
                         reply_markup=contacts_kb)


@user_router.message(F.text == "Информация о компании🪬")
async def main_menu_info(message: Message):
    image = "https://img01.rl0.ru/afisha/e750x-i/daily.afisha.ru/uploads/images/b/25/b2586f8eb5561542e587aded807478e8.jpg"

    async with ChatActionSender.upload_photo(
            bot=message.bot,
            chat_id=message.chat.id,
    ):
        await asyncio.sleep(2)  # чтобы посмотреть на отработку ChatActionSender
        await message.answer_photo(photo=image, caption="какой-нибудь красивый текст с картинкой - (любые)",
                                   reply_markup=main_menu_kb, parse_mode=ParseMode.HTML)
