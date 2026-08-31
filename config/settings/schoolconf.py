from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Env-driven path to the school data YAML
# ---------------------------------------------------------------------------


class SchoolDataPathSettings(BaseSettings):
    """Reads the path to school-data.yaml from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    school_data_path: Path = Field(default=Path("school-data.yaml"))


# ---------------------------------------------------------------------------
# Pydantic models mirroring school-data.yaml
# ---------------------------------------------------------------------------


class Coordinates(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class Address(BaseModel):
    street: str = ""
    village: str = ""
    district: str = ""
    city: str = ""
    province: str = ""
    postal_code: str = ""
    coordinates: Coordinates = Field(default_factory=Coordinates)


class Contact(BaseModel):
    phone: str = ""
    fax: str = ""
    email: str = ""
    website: str = ""


class Accreditation(BaseModel):
    status: str = Field(default="", max_length=20)
    number: str = ""
    valid_until: str = ""


class AcademicYear(BaseModel):
    current: str = Field(
        pattern=r"^\d{4}/\d{4}$",
        examples=["2025/2026"],
    )
    start_month: int = Field(ge=1, le=12)
    end_month: int = Field(ge=1, le=12)
    semesters: int = Field(ge=1, le=4, default=2)


class NumberFormat(BaseModel):
    decimal_separator: str = ","
    thousands_separator: str = "."
    decimals: int = Field(ge=0, le=10, default=2)


class System(BaseModel):
    timezone: str = "Asia/Jakarta"
    language: str = "id-ID"
    currency: str = "IDR"
    date_format: str = "dd-MM-yyyy"
    datetime_format: str = "dd-MM-yyyy HH:mm"
    number_format: NumberFormat = Field(default_factory=NumberFormat)


class Grading(BaseModel):
    grade_scale: str = Field(default="numeric")
    min_passing_score: int = Field(ge=0, le=100, default=70)
    report_format: str = Field(default="smp_2013")


class Term(BaseModel):
    name: str
    code: str
    months: list[int] = Field(min_length=1, max_length=12)

    @field_validator("months")
    @classmethod
    def months_in_range(cls, v: list[int]) -> list[int]:
        if not all(1 <= m <= 12 for m in v):
            raise ValueError("All months must be between 1 and 12")
        return sorted(v)


class SchoolIdentity(BaseModel):
    name: str
    short_name: str = ""
    npsn: str = Field(
        pattern=r"^\d{8}$",
        examples=["12345678"],
    )
    nss: str = ""
    nis: str = ""

    address: Address = Field(default_factory=Address)
    contact: Contact = Field(default_factory=Contact)

    school_level: str = Field(
        default="SD",
        pattern=r"^(SD|SMP|SMA|SMK)$",
    )
    status: str = Field(default="negeri", pattern=r"^(negeri|swasta)$")

    accreditation: Accreditation = Field(default_factory=Accreditation)
    academic_year: AcademicYear
    grading: Grading = Field(default_factory=Grading)
    terms: list[Term]

    education_level: str = Field(
        default="dasar",
        pattern=r"^(dasar|menengah_pertama|menengah_atas)$",
    )
    ministry_code: str = "KEMENDIKBUD"
    regional_code: str = Field(default="01", max_length=10)
    school_logo_url: str = ""
    stamp_url: str = ""

    @model_validator(mode="after")
    def validate_academic_year_months(self) -> "SchoolIdentity":
        if self.academic_year.start_month == self.academic_year.end_month:
            raise ValueError("start_month and end_month must differ")
        return self


class Headmaster(BaseModel):
    name: str = ""
    nip: str = ""
    nuptk: str = ""
    gender: str = ""
    phone: str = ""
    email: str = ""

    @model_validator(mode="after")
    def require_name_if_nip(self) -> "Headmaster":
        if self.nip and not self.name:
            raise ValueError("name is required when nip is set")
        return self


class AdminOfficer(BaseModel):
    name: str = ""
    nip: str = ""
    phone: str = ""
    email: str = ""


class SchoolConfigData(BaseModel):
    school: SchoolIdentity
    headmaster: Headmaster = Field(default_factory=Headmaster)
    admin_officer: AdminOfficer = Field(default_factory=AdminOfficer)
    system: System = Field(default_factory=System)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _resolve_yaml_path(raw: Path | str | None) -> Path:
    """Resolve the YAML path relative to the project root (two levels up from config/)."""
    base = Path(__file__).resolve().parent.parent
    path = Path(raw) if raw else base / "school-data.yaml"
    if not path.is_absolute():
        path = base / path
    if not path.exists():
        raise FileNotFoundError(
            f"School data file not found: {path}. "
            "Set SCHOOL_DATA_PATH in .env to point to your school-data.yaml."
        )
    return path


def load_school_config(path: Path | str | None = None) -> SchoolConfigData:
    settings = SchoolDataPathSettings()
    yaml_path = _resolve_yaml_path(path or settings.school_data_path)

    logger.info("loading_school_config", yaml_path=str(yaml_path))

    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if raw is None:
        raise ValueError(f"school-data.yaml is empty: {yaml_path}")

    config = SchoolConfigData.model_validate(raw)
    logger.info(
        "school_config_validated",
        school_name=config.school.name,
        school_level=config.school.school_level,
        academic_year=config.school.academic_year.current,
    )
    return config


# ---------------------------------------------------------------------------
# Module-level singleton — loads once at import time
# ---------------------------------------------------------------------------

try:
    _school_config: SchoolConfigData | None = load_school_config()
except Exception:
    _school_config = None


def get_school_config() -> SchoolConfigData:
    global _school_config  # noqa: PLW0603
    if _school_config is None:
        _school_config = load_school_config()
    return _school_config


# Convenience alias — preferred import for most use sites
school_config = get_school_config()
