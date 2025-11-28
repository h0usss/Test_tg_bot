from datetime import datetime

from sqlalchemy import text, ForeignKey, ARRAY, String, BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from src.database.database import Base
from src.database.enums import Gender


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BIGINT)

    fio: Mapped[str]
    is_admin: Mapped[bool]
    phone_number: Mapped[str]
    birthday: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    def __repr__(self):
        return f"User( id = {self.id}, " \
               f"tg_id = {self.tg_id}, " \
               f"fio = {self.fio}, " \
               f"phone_number = {self.phone_number}, " \
               f"birthday = {self.birthday}, " \
               f"created_at = {self.created_at} )"


class Application(Base):
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id'))

    gender: Mapped[Gender]
    cat_photo_id: Mapped[str]
    love: Mapped[Gender]
    car: Mapped[list[str]] = mapped_column(ARRAY(String))

    def __repr__(self):
        return f"Application( id = {self.id}, " \
               f"user_id = {self.user_id}, " \
               f"gender = {self.gender}, " \
               f"cat_photo_id = {self.cat_photo_id}, " \
               f"love = {self.love}, " \
               f"car = {self.car} )"
