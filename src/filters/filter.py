from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dal import UserDal


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery, session: AsyncSession, state: FSMContext) -> bool:
        user = await UserDal.get_user(session=session, tg_id=message.from_user.id)
        if user:
            return user.is_admin
        return False
