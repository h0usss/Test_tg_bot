from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from src.config import USER_COUNT_IN_ONE_PAGE
from src.database.dto import UserDto
from src.database.enums import Gender, Cars

phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text="Отправить свой номерочек",
            request_contact=True,
        )]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбирай, Нео.."
)

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оставить заявку📝")],
        [KeyboardButton(text="Контакты")],
        [KeyboardButton(text="Информация о компании🪬")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбирай, Нео.."
)

contacts_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сайт🌐", url="https://cat-bounce.com/")]
    ]
)

application_cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Отмена",
                callback_data="cancel"
            )
        ]
    ],
    input_field_placeholder="Выбирай, Нео.."
)

admin_command_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Статистика📑", callback_data="admin_statistics"),
            InlineKeyboardButton(text="Рассылка🌐", callback_data="admin_mailing"),
        ],
        [
            InlineKeyboardButton(text="Пользователи🙆‍♂️", callback_data="admin_users_1")
        ]
    ]
)

admin_command_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="admin_back"),
        ]
    ]
)

admin_command_mailing_confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back"),
            InlineKeyboardButton(text="✅ Всё гуд", callback_data="admin_send"),
        ]
    ]
)

admin_command_back_to_main_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Вернуться", callback_data="admin_back"),
        ]
    ]
)


async def application_gender_reply_kb() -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()

    (kb_builder
     .add(*[KeyboardButton(text=gender.capitalize()) for gender in Gender.get_list_names()])
     .adjust(2)
     )
    kb_builder.row(KeyboardButton(text="Отмена"))

    return kb_builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выбирай, Нео.."
    )


async def application_love_inline_kb() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    (kb_builder
     .add(*[InlineKeyboardButton(
        callback_data=f"love_{gender}",
        text=gender.capitalize()) for gender in Gender.get_list_names()]
          )
     .adjust(2)
     )
    kb_builder.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

    return kb_builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder="Выбирай, Нео.."
    )


async def application_car_kb(check: list[bool] = None) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    cars = Cars.get_list_names()

    check = check if check else [False] * len(cars)

    for i in range(len(cars)):
        check_text = ""
        if check[i]:
            check_text = "✅"

        kb_builder.add(
            InlineKeyboardButton(
                callback_data=f"{check_text}car_{cars[i]}",
                text=f"{check_text}{cars[i]}"
            )
        )

    (kb_builder
     .add(InlineKeyboardButton(
        callback_data="done_car",
        text="Подтвердить"))
     .adjust(2)
     )

    kb_builder.row(InlineKeyboardButton(text="Отмена", callback_data="cancel"))

    return kb_builder.as_markup()


async def admin_user_list_main_kb(users: list[UserDto], page: int, count_page: int):
    kb_builder = InlineKeyboardBuilder()

    for user in users:
        kb_builder.row(InlineKeyboardButton(
            text=f"{user.id}: {user.fio}",
            callback_data=f"admin_user_{user.id}"
        ))

    for i in range(len(users) % USER_COUNT_IN_ONE_PAGE != 0):
        kb_builder.row(InlineKeyboardButton(
            text=" ",
            callback_data="ignore"
        ))

    pagination_button = [
        InlineKeyboardButton(
            text="⬅️",
            callback_data=f"admin_users_{page - 1}" if page > 1 else f"admin_users_{count_page}"
        ),
        InlineKeyboardButton(
            text=f"{page} | {count_page}",
            callback_data="ignore"
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"admin_users_{page + 1}" if page < count_page else "admin_users_1"
        )
    ]

    kb_builder.row(*pagination_button)
    kb_builder.row(InlineKeyboardButton(text="На главную", callback_data=f"admin_back"))

    return kb_builder.as_markup()


async def admin_user_list_user_kb(last_visit_page: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="К списку", callback_data=f"admin_users_{last_visit_page}"),
                InlineKeyboardButton(text="На главную", callback_data=f"admin_back"),
            ]
        ]
    )
