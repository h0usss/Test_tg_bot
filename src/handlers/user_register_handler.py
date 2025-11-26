import re
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dao import UserDao
from src.database.dto import UserRegisterDto
from src.handlers.user_handler import main_menu
from src.keyboards.keyboard import phone_kb
from src.states.state import Register


register_router = Router()

@register_router.message(Register.fio, F.text)
async def register_save_fio(message: Message, state: FSMContext):
    if bool(re.search(r'[^a-zA-Zа-яА-ЯёЁ\s]', message.text)):
        await message.answer(text="Простофиля, ФИО не может содержать что то, кроме букв. Попробуй ещё раз💋")
        return

    if len(message.text.split()) != 3:
        await message.answer(text="Дуралей, ФИО состоит из 3х слов, попробуй ещё раз💋")
        return

    await state.update_data(Fio=message.text)
    await state.set_state(Register.birthday)
    await message.answer(text="Отлично, укажите свою дату рождения в формате ДД.ММ.ГГГГ")


@register_router.message(Register.birthday)
async def register_save_birthday(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text, "%d.%m.%Y")
    except ValueError:
        await message.answer(text="Дурашка, некорректно написал дату, попробуй ещё раз💋")
        return

    await state.update_data(Birthday=message.text)
    await state.set_state(Register.phone)
    await message.answer(
        text="Осталось последнее, номер телефона. Просто отправь мне свой контактик💋",
        reply_markup=phone_kb
    )


@register_router.message(Register.phone, F.contact)
async def register_save_phone_contact(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(Phone=message.contact.phone_number)
    await create_and_save_user(message, session, state)


@register_router.message(Register.phone)
async def register_save_phone(message: Message, session: AsyncSession, state: FSMContext):
    phone_regex = r"^\+?(7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$"

    if not re.fullmatch(phone_regex, message.text):
        await message.answer(
            text="Постарайся ещё раз, только в этот раз правильно напиши номер или отправь контакт💋",
            reply_markup=phone_kb
        )
        return

    await state.update_data(Phone=message.text)
    await create_and_save_user(message, session, state)


async def create_and_save_user(message, session, state):
    data = await state.get_data()
    new_user = UserRegisterDto(
        tg_id=message.from_user.id,
        fio=data["Fio"],
        is_admin=False,
        birthday=datetime.strptime(data["Birthday"], "%d.%m.%Y"),
        phone_number=data["Phone"],
    )
    await UserDao.insert(session, new_user)
    await state.clear()
    await message.answer(text="Атлична, твои данные уже улетели к мошенникам💋")
    await main_menu(message, state, session)
