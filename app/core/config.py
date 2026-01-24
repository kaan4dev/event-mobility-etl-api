from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "mobility"
    db_user: str = "mobility"
    db_password: str = "mobility"

    max_errors: int = 200
    strict_mode: bool = False

    @property
    def db_url(self) -> str:
        # psycopg v3 + SQLAlchemy
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
