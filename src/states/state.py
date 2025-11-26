from aiogram.fsm.state import StatesGroup, State


class Register(StatesGroup):
    fio = State()
    phone = State()
    birthday = State()


class Application(StatesGroup):
    car = State()
    love = State()
    start = State()
    gender = State()
    cat_photo_id = State()


class Mailing(StatesGroup):
    sending_data = State()
    confirmation = State()
