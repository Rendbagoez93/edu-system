from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBEngineEnum(StrEnum):
    """Supported database engines."""

    SQLITE = "django.db.backends.sqlite3"
    POSTGRES = "django.db.backends.postgresql"


class BaseDatabaseSettings(BaseSettings):
    """Base database settings shared across all database types."""

    engine: DBEngineEnum = DBEngineEnum.SQLITE

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        extra="ignore",
        frozen=True,
        alias_generator=lambda field_name: field_name.upper(),
        populate_by_name=True,
        env_file=".env",
    )

    @field_validator("engine", mode="before")
    @classmethod
    def validate_engine(cls, v: Any) -> DBEngineEnum:
        if isinstance(v, DBEngineEnum):
            return v

        valid_names = [member.name for member in DBEngineEnum]
        valid_values = [member.value for member in DBEngineEnum]

        if isinstance(v, str):
            # Try to match by name (case-insensitive)
            try:
                return DBEngineEnum[v.upper()]
            except KeyError:
                pass

            # Try to match by value
            for enum_member in DBEngineEnum:
                if v == enum_member.value:
                    return enum_member

        raise PydanticCustomError(
            "enum",
            f"Input should be one of the enum names: {valid_names} or one of the enum values: {valid_values}",
            {
                "input": v,
                "valid_names": valid_names,
                "valid_values": valid_values,
            },
        )


class SqliteDatabaseSettings(BaseDatabaseSettings):
    """Settings for SQLite database."""

    engine: DBEngineEnum = DBEngineEnum.SQLITE
    name: str = (Path(__file__).resolve().parent.parent.parent / "db.sqlite3").as_posix()

    @property
    def sqlite_name(self) -> str:
        """Alias for `name`, used by local.py."""
        return self.name


class PostgresDatabaseSettings(BaseDatabaseSettings):
    """Settings for PostgreSQL database."""

    engine: DBEngineEnum = DBEngineEnum.POSTGRES
    port: int = 5432
    host: str = "localhost"
    password: str = "postgres"
    user: str = "postgres"
    name: str = "school_management"


class DjangoDatabases(BaseModel):
    """Django database settings container."""

    default: PostgresDatabaseSettings | SqliteDatabaseSettings


# ---------------------------------------------------------------------------
# Module-level singletons — used by production.py and local.py
# ---------------------------------------------------------------------------

# Read DATABASE_ENGINE directly from env so we pick the right singleton before
# any default kicks in. If unset, default to SQLite (safer for local dev).
import os as _os

_engine_str = _os.environ.get("DATABASE_ENGINE", "").upper()
if _engine_str == "POSTGRES":
    db_settings: PostgresDatabaseSettings | SqliteDatabaseSettings = PostgresDatabaseSettings()
else:
    db_settings = SqliteDatabaseSettings()


class DatabaseConnectionSettings(BaseSettings):
    """Connection-level settings shared by all database backends."""

    model_config = SettingsConfigDict(env_prefix="DATABASE_", extra="ignore")

    conn_max_age: int = Field(default=600, description="Connection lifetime in seconds (0=close after each request)")
    conn_health_checks: bool = Field(default=False, description="Check connection health before reuse")
    atomic_requests: bool = Field(default=False, description="Wrap each request in a transaction")


db_conn_settings = DatabaseConnectionSettings()
