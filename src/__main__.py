import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from config import config
from handlers.user_handler import user_router
from src.database.dal import UserDal
from src.database.database import session_factory, create_db
from src.filters.filter import AdminFilter
from src.handlers.admin_handler import admin_router
from src.handlers.admin_mailing_handler import mailing_router
from src.handlers.admin_user_list_handler import list_router
from src.handlers.user_application_handler import application_router
from src.handlers.user_register_handler import register_router
from src.middleware.middleware import DbSessionMiddleware


async def setup_bot(bot: Bot):
    await bot.set_my_commands(commands=[],scope=BotCommandScopeDefault())

    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="Запустить бота")
        ],
        scope=BotCommandScopeDefault()
    )
    admins_ids = []

    for admin_id in config.ADMIN_IDS.strip().split(';'):
        if admin_id == "":
            continue
        try:
            admins_ids.append(int(admin_id))
        except ValueError:
            logging.error(f"ID {admin_id} некорректен")

    async with session_factory() as session:

        await UserDal.set_all_user_non_admin(session)

        for admin_id in admins_ids:
            user = await UserDal.get_user(
                session=session,
                tg_id=admin_id)
            if user:
                user.is_admin = True

        await session.commit()

    for admin_id in admins_ids:
        try:
            await bot.set_my_commands(
                commands=[
                    BotCommand(command="start", description="Запустить бота"),
                    BotCommand(command="admin", description="Админские штучки"),
                ],
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logging.error(f"Не можем достучаться до админа c ID {admin_id}")


async def main():
    bot = Bot(token=config.TOKEN.get_secret_value())
    dp = Dispatcher()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    await create_db()
    await setup_bot(bot)

    admin_routers = [admin_router, mailing_router, list_router]
    dp.include_routers(*[user_router, *admin_routers, register_router, application_router ])

    for router in admin_routers:
        router.message.filter(AdminFilter())
        router.callback_query.filter(AdminFilter())

    dp.update.outer_middleware(DbSessionMiddleware(session_factory=session_factory))
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Completion of work, bye-bye")
