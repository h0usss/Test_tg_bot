from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.sql.functions import func

from src.database.dto import UserRegisterDto, ApplicationDto, UserDto
from src.database.model import User, Application


class UserDal:

    @staticmethod
    async def insert(session: AsyncSession, dto: UserRegisterDto):
        session.add(User(**dto.model_dump()))
        await session.commit()

    @staticmethod
    async def get_user(session: AsyncSession, tg_id: int = None, user_id: int = None) -> User | None:
        if tg_id:
            query = select(User).filter_by(tg_id=tg_id)
        elif user_id:
            query = select(User).filter_by(id=user_id)
        else:
            return None

        user = await session.scalar(query)
        return user

    @staticmethod
    async def get_all_admins(session: AsyncSession) -> list[int]:
        query = select(User.tg_id).filter_by(is_admin=True)
        admins = await session.scalars(query)
        return list(admins.all())

    @staticmethod
    async def get_count_user(session: AsyncSession) -> int:
        query = select(func.count()).select_from(User)
        user_count = await session.scalar(query)
        return user_count if user_count else 0

    @staticmethod
    async def get_all_user_tg_id(session: AsyncSession) -> list[int]:
        query = select(User.tg_id).filter_by(is_admin=False)
        user_tg_ids = await session.scalars(query)
        return list(user_tg_ids)

    @staticmethod
    async def get_several_users(session: AsyncSession, return_count: int, page: int) -> list[UserDto]:
        query = select(User).order_by(User.id).offset((page - 1) * return_count).limit(return_count)
        all_users = await session.scalars(query)

        result = [UserDto.model_validate(user) for user in all_users.all()]
        return result

    @staticmethod
    async def set_all_user_non_admin(session: AsyncSession):
        query = update(User).values(is_admin=False)
        await session.execute(query)
        await session.commit()


class ApplicationDal:

    @staticmethod
    async def insert(session: AsyncSession, dto: ApplicationDto) -> int:
        user = await UserDal.get_user(
            session=session,
            tg_id=dto.tg_id
        )

        dto.user_id = getattr(user, 'id')
        new_application = Application(**dto.model_dump(exclude={'tg_id'}))
        session.add(new_application)

        await session.commit()
        await session.refresh(new_application, attribute_names=["id"])
        return new_application.id

    @staticmethod
    async def get_application(session: AsyncSession, application_id: int) -> Application:
        query = select(Application).filter_by(id=application_id)
        application = await session.scalar(query)
        return application

    @staticmethod
    async def get_count_application(session: AsyncSession) -> int:
        query = select(func.count()).select_from(Application)
        application_count = await session.scalar(query)
        return application_count if application_count else 0
