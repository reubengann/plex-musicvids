from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    vids_folder: Optional[str] = None
    dummy_root: Optional[str] = None
    playlist_name: Optional[str] = None
    ffmpeg_bin: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings.model_validate({})
