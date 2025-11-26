from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import APPLICATION_START
from src.database.dao import ApplicationDao
from src.database.dto import ApplicationDto
from src.database.enums import Gender, Cars
from src.handlers.admin_handler import send_application_all_admins
from src.keyboards.keyboard import application_gender_reply_kb, application_love_inline_kb, application_car_kb, \
    main_menu_kb, application_cancel_kb
from src.states.state import Application


application_router = Router()

@application_router.message(F.text == "Отмена")
async def application_cancel_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Выбирай что делать дальше🥰",
                                  reply_markup=main_menu_kb)

@application_router.callback_query(F.data == "cancel")
async def application_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(text="Выбирай что делать дальше🥰",
                                  reply_markup=main_menu_kb)


@application_router.message(Application.start)
async def application_start(message: Message, state: FSMContext):
    await state.set_state(Application.gender)
    await message.answer(
        text=APPLICATION_START,
        reply_markup=await application_gender_reply_kb()
    )


@application_router.message(Application.gender)
async def application_save_gender(message: Message, state: FSMContext):
    if message.text.lower() in Gender.get_list_names():
        await state.set_state(Application.cat_photo_id)
        await state.update_data(gender=message.text.lower())
        await message.answer(
            text="Отлично, теперь отправь фото самого крутого кота🐱",
            reply_markup=application_cancel_kb
        )
    else:
        await message.answer(
            text="Сорянчики, такие гендеры мы пока не знаем, выбирай из того что дают💅",
            reply_markup=await application_gender_reply_kb()
        )


@application_router.message(Application.cat_photo_id)
async def application_save_photo(message: Message, state: FSMContext):
    if message.content_type != ContentType.PHOTO:
        await message.answer(
            text="Круто конечно, но нам нужна фоточка📷",
            reply_markup=application_cancel_kb
        )
    else:
        await state.set_state(Application.love)
        await state.update_data(cat_photo_id=message.photo[-1].file_id)
        await message.answer(
            text="Вот это милота конечно🥰 Теперь выбери пол, который тебе нравится",
            reply_markup=await application_love_inline_kb()
        )


@application_router.message(Application.love)
async def application_save_love_send_text(message: Message):
    await message.delete()


@application_router.callback_query(Application.love)
async def application_save_love(callback: CallbackQuery, state: FSMContext):
    await state.update_data(love=callback.data.replace('love_', '').lower())
    await state.set_state(Application.car)

    await state.update_data(car_choice=[False] * len(Cars.get_list_names()))
    await application_car_message(
        callback=callback,
        state=state
    )


async def application_car_message(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bullying = ""
    current_choice = data["car_choice"]

    if data["gender"] == Gender.male.name and data["love"] == Gender.male.name:
        bullying = ", геюга👀"
    if data["gender"] == Gender.female.name and data["love"] == Gender.female.name:
        bullying = ", лезбушка👀"

    await callback.message.edit_text(
        text=f"Отлично{bullying}\nТеперь выбери машины, которые тебе нравятся🚗",
        reply_markup=await application_car_kb(current_choice)
    )


@application_router.callback_query(
    Application.car,
    F.data.startswith("car_") | F.data.startswith("check_car_")
)
async def application_car_choice(callback: CallbackQuery, state: FSMContext):
    cars = Cars.get_list_names()
    data = await state.get_data()
    current_choice = data["car_choice"]

    if callback.data.startswith('car_'):
        car_name = callback.data.replace('car_', '')
        new_state = True
    else:
        car_name = callback.data.replace('check_car_', '')
        new_state = False

    try:
        index = cars.index(car_name)
        current_choice[index] = new_state
        await state.update_data(car_choice=current_choice)
        await application_car_message(
            callback=callback,
            state=state
        )

    except ValueError:
        await callback.answer("Неизвестный автомобиль.")


@application_router.callback_query(Application.car, F.data == "done_car")
async def application_save_car(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    all_cars = Cars.get_list_names()
    cars = [all_cars[i] for i in range(len(all_cars)) if data["car_choice"][i]]

    new_application = ApplicationDto(
        tg_id=callback.from_user.id,
        gender=data["gender"],
        cat_photo_id=data["cat_photo_id"],
        love=data["love"],
        car=cars
    )
    application_id = await ApplicationDao.insert(session=session, dto=new_application)

    await state.clear()
    await callback.message.edit_text(
        text=f"Ваша заявка №{application_id} сформирована"
    )
    await callback.message.answer(text="Выбирай что делать дальше🥰",
                                  reply_markup=main_menu_kb)

    await send_application_all_admins(
        session=session,
        bot=callback.bot,
        application_id=application_id
    )
