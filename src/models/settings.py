from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    QDRANT__SERVICE__API_KEY: str
    QDRANT__SERVICE__HOST: str
    QDRANT__SERVICE__PORT: int