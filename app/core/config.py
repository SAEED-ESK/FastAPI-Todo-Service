from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_JWT_SECRET_KEY: str = "todo"

    model_config = SettingsConfigDict(
        env_file=".env"
    )

# Instantiate settings (values are loaded from env variables automatically)
settings = Settings()