from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Notification Service"

    DATABASE_URL: str = "sqlite:///./notification.db"

    # Internal service authentication
    INTERNAL_API_KEY: str

    # SMTP Configuration
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str

    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()