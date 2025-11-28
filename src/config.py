from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    TOKEN: SecretStr

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

    ADMIN_IDS: str


    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8"
    )

    @property
    def DB_URL(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


config = Config()

USER_COUNT_IN_ONE_PAGE = 2

CONTACTS = """Контакты:
    - Наш сайт 🌐: https://cat-bounce.com/
    - Номер 📱: +1231230912839102389012839018
    - Почта 📭: Почта
"""

APPLICATION_START = """Оформление заявки на 何か
Для начала выберите свой пол
"""

ADMIN_COMMAND = "Дорогой Одмен, выбери действие"

ADMIN_WRITE_A_TEXT = "Введите сообщение для массовой рассылки ( фото + текст, фото или текст )✍️"
