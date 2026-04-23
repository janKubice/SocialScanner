from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    openai_api_key: str
    apify_token: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()