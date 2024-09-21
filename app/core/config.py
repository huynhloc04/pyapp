from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn
from functools import cached_property
from pydantic import PostgresDsn, computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    VERSION: str = Field("1.0")
    PROJECT_NAME: str = Field("Standard FastAPI application.")

    HOST: str
    PORT: str

    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("postgres", env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("postgres", env="POSTGRES_DB")
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_ECHO: bool = Field(False, env="POSTGRES_ECHO")
    POSTGRES_POOL_SIZE: int = Field(10, env="POSTGRES_POOL_SIZE")

    ACCESS_TOKEN_EXPIRE_MINUTES: str
    REFRESH_TOKEN_EXPIRE_MINUTES: str
    ALGORITHM: str

    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    #   Single Sign On (SSO)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str

    # ShipEngine
    SHIPENGINE_API_KEY: str
    SHIPENGINE_URL: str

    @computed_field
    @cached_property
    def DATABASE_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


settings = Settings()
