from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ALGORITHM: str
    ORIGINS:str 
    ALGORITHM : str
    ORIGINS : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    model_config =SettingsConfigDict(env_file="../.env",env_file_encoding="utf-8",extra="ignore")


settings = Settings()