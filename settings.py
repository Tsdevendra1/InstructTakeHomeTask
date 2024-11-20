from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    OPENAI_API_KEY: str

settings = Settings()
