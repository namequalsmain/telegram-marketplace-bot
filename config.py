from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = getenv("BOT_TOKEN", "")

    DB_USER: str = getenv("DB_USER", "postgres")
    DB_PASS: str = getenv("DB_PASS", "")
    DB_HOST: str = getenv("DB_HOST", "localhost")
    DB_PORT: str = getenv("DB_PORT", "5432")
    DB_NAME: str = getenv("DB_NAME", "market_db")
    # Set DB_SSL=require for managed Postgres (Neon, Supabase, etc.)
    DB_SSL: str = getenv("DB_SSL", "")

    MAIN_ADMIN_ID: int = int(getenv("MAIN_ADMIN_ID") or 0)

    @property
    def DSN(self) -> str:
        url = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        if self.DB_SSL:
            url += f"?ssl={self.DB_SSL}"
        return url


settings = Settings()
