"""General configuration.

Config: Bot Config
"""

# ruff: noqa: ARG003
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
    HOSTNAME: str = "0.0.0.0"  # noqa: S104
    HTTP_SERVER: bool = True

    API_ID: int = 25482744
    API_HASH: str = "e032d6e5c05a5d0bfe691480541d64f4"
    BOT_TOKEN: str = "7999015273:AAGjQtwxPbaOWofV9YYH2PZeGV730ck3h_w"
    BOT_WORKER: int = 8
    BOT_SESSION: str = "Zaws-File-Share"
    BOT_MAX_MESSAGE_CACHE_SIZE: int = 100

    MONGO_DB_URL: MongoSRVDsn = "mongodb+srv://emailbot:utkarsh2008@cluster0.08udh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    MONGO_DB_NAME: str = "Zaws-File-Share"

    # Bot main config
    RATE_LIMITER: bool = True
    BACKUP_CHANNEL: int = -1002485552269
    ROOT_ADMINS_ID: list[int] = [2009509228, 7758708579]
    PRIVATE_REQUEST: bool = False
    PROTECT_CONTENT: bool = True
    FORCE_SUB_CHANNELS: list[int] = [-1002209844539]
    AUTO_GENERATE_LINK: bool = True

    # Injected Config
    channels_n_invite: dict[str, ChannelInfo] = {}

    model_config = SettingsConfigDict(
        env_file=f"{BASE_PATH}/.env",
    )

    @field_validator("ROOT_ADMINS_ID", "FORCE_SUB_CHANNELS", mode="before")
    @classmethod
    def convert_int_to_list(cls, value: int | list[int]) -> list[int]:
        if isinstance(value, int):
            return [value]
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
    config = Config()  # type: ignore[reportCallIssue]
except (ValidationError, SettingsError):
    logging.exception("Configuration Error")
    sys.exit(1)
