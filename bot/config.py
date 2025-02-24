"""General configuration.

Config: Bot Config
"""

import logging
import sys
from pathlib import Path
from typing import Annotated

from pydantic import ValidationError, field_validator
from pydantic.networks import UrlConstraints
from pydantic_core import MultiHostUrl
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pydantic_settings.sources import SettingsError
from typing_extensions import TypedDict

MongoSRVDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=["mongodb+srv"])]
BASE_PATH = Path(__file__).parent.parent


class ChannelInfo(TypedDict):
    is_private: bool
    invite_link: str
    channel_id: int


class Config(BaseSettings):
    """A general configuration setup to read either .env or environment keys."""

    # Bot deploy config
    PORT: int = 8080
    HOSTNAME: str = "0.0.0.0"
    HTTP_SERVER: bool = False

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
    BOT_WORKER: int
    BOT_SESSION: str
    BOT_MAX_MESSAGE_CACHE_SIZE: int

    MONGO_DB_URL: MongoSRVDsn
    MONGO_DB_NAME: str

    # Bot main config
    RATE_LIMITER: bool = True
    BACKUP_CHANNEL: int
    ROOT_ADMINS_ID: list[int]
    PRIVATE_REQUEST: bool
    PROTECT_CONTENT: bool
    FORCE_SUB_CHANNELS: list[int]
    AUTO_GENERATE_LINK: bool

    # Injected Config
    channels_n_invite: dict[str, ChannelInfo] = {}

    model_config = SettingsConfigDict(
        env_file=f"{BASE_PATH}/.env",
    )

    @field_validator("ROOT_ADMINS_ID", "FORCE_SUB_CHANNELS", mode="before")
    @classmethod
    def parse_list(cls, value: str | list[int]) -> list[int]:
        """Convert a comma-separated string to a list of integers."""
        if isinstance(value, str):
            try:
                return [int(x.strip()) for x in value.split(",") if x.strip().isdigit()]
            except ValueError:
                raise ValueError(f"Invalid format for list[int]: {value}")
        return value

    @field_validator("channels_n_invite", mode="before")
    @classmethod
    def ignore_keys(cls, value: dict[str, ChannelInfo]) -> dict[str, ChannelInfo]:
        return {}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            DotEnvSettingsSource(settings_cls),
            EnvSettingsSource(settings_cls),
        )


try:
    config = Config()
except (ValidationError, SettingsError):
    logging.exception("Configuration Error")
    sys.exit(1)
