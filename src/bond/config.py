"""Validated database configuration without printable credentials."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="BOND_DB_",
        extra="ignore",
        frozen=True,
    )

    host: str = Field(min_length=1, repr=False)
    port: int = Field(default=5432, ge=1, le=65535)
    name: str = Field(default="postgres", min_length=1, repr=False)
    user: str = Field(min_length=1, repr=False)
    password: SecretStr = Field(min_length=1, repr=False)
