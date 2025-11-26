from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    TOKEN: SecretStr

    DB_HOST: SecretStr  # Не уверен что они должны быть секретными
    DB_PORT: SecretStr
    DB_USER: SecretStr
    DB_PASS: SecretStr
    DB_NAME: SecretStr

    ADMIN_IDS: SecretStr


    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8"
    )

    @property
    def DB_URL(self):
        return (f"postgresql+asyncpg://{self.DB_USER.get_secret_value()}:{self.DB_PASS.get_secret_value()}"
                f"@{self.DB_HOST.get_secret_value()}:{self.DB_PORT.get_secret_value()}/{self.DB_NAME.get_secret_value()}")



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
