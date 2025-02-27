# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_secret: str
    verify_token: str
    gemini_api_key: str
    celery_broker_url: str 
    celery_result_backend: str
    accounts_json: str = '{}'  # JSON string for account credentials
    webhook_file: str = "webhook_events.json"
    model_name: str = "gemini-1.5-flash"

    default_dm_response_positive: str = "Thanks for your kind words! We appreciate your support."
    default_dm_response_negative: str = "We are sorry to hear you're not satisfied. Please tell us more about this so that we can improve."
    default_comment_response_positive: str = "Thanks for your kind words! We appreciate your support."
    default_comment_response_negative: str = "We are sorry to hear you're not satisfied. Please tell us more about this so that we can improve."

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()