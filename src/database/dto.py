from datetime import datetime

from pydantic import BaseModel, Field, PositiveInt

from src.database.enums import Gender


class UserDto(BaseModel):
    id: PositiveInt
    tg_id: PositiveInt

    is_admin: bool
    phone_number: str
    birthday: datetime
    created_at: datetime
    fio: str = Field(max_length=255)

    model_config = {
        "from_attributes": True
    }


class UserRegisterDto(BaseModel):
    tg_id: PositiveInt

    phone_number: str
    is_admin: bool
    birthday: datetime
    fio: str = Field(max_length=255)


class ApplicationDto(BaseModel):
    tg_id: PositiveInt
    user_id: PositiveInt = -1

    gender: Gender
    cat_photo_id: str
    love: Gender
    car: list[str]
