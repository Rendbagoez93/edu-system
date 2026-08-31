from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from config.settings.databases import db_conn_settings, db_settings
from config.settings.envcommon import env_common
from config.settings.logging import configure_logging

# Activate logging first
configure_logging(debug=False)

# ---------------------------------------------------------------------------
# Environment guard — this file is only for production
# ---------------------------------------------------------------------------

if not env_common.is_production:
    raise RuntimeError(
        "config/settings/production.py is for production deployments only. "
        "Use config/settings/local.py for local development."
    )

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

SECRET_KEY = env_common.secret_key
DEBUG = False
ALLOWED_HOSTS = env_common.allowed_hosts
BASE_DIR = env_common.base_dir

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "core.User"

# ---------------------------------------------------------------------------
# Database — PostgreSQL (see databases.py)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": db_settings.engine.value,
        "NAME": db_settings.name,
        "USER": db_settings.user,
        "PASSWORD": db_settings.password,
        "HOST": db_settings.host,
        "PORT": db_settings.port,
        "CONN_MAX_AGE": db_conn_settings.conn_max_age,
        "CONN_HEALTH_CHECKS": db_conn_settings.conn_health_checks,
        "ATOMIC_REQUESTS": db_conn_settings.atomic_requests,
    }
}

# ---------------------------------------------------------------------------
# Installed apps
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django built-ins
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
    # Layer 0 — Foundation
    "apps.shared.apps.SharedConfig",
    "apps.core.apps.CoreConfig",
    # Layer 1 — Structure
    "apps.academic_structure.apps.AcademicStructureConfig",
    # Layer 2 — Entities
    "apps.teachers.apps.TeachersConfig",
    "apps.students.apps.StudentsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "id-ID"
TIME_ZONE = env_common.app_timezone
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static / Media files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Email — SMTP backend (configure via .env)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
DEFAULT_FROM_EMAIL = "noreply@edusys.school"

# ---------------------------------------------------------------------------
# Caches — Redis (see .env for REDIS_HOST, REDIS_PORT)
# ---------------------------------------------------------------------------


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(default="localhost")
    port: int = Field(default=6379)
    db: int = Field(default=0)

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


redis_settings = RedisSettings()

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_settings.url,
    }
}

# ---------------------------------------------------------------------------
# Celery + Redis broker
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = redis_settings.url
CELERY_RESULT_BACKEND = redis_settings.url
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = env_common.app_timezone
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# ---------------------------------------------------------------------------
# REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": env_common.app_name,
    "DESCRIPTION": "School Management System API — production",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {"name": "core", "description": "School identity, academic year, users"},
        {"name": "academic_structure", "description": "Grade levels, subjects, class sections"},
        {"name": "teachers", "description": "Teacher profiles"},
        {"name": "students", "description": "Student profiles, enrollment, bulk import"},
        {"name": "schedules", "description": "Time slots, conflict detection"},
        {"name": "grade_management", "description": "Tingkat ↔ Teacher ↔ Subject ↔ Schedule assignment"},
        {"name": "assessment", "description": "Scores, report cards"},
        {"name": "onboarding", "description": "First-run wizard"},
    ],
}

# ---------------------------------------------------------------------------
# Security — strict headers for production
# ---------------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# ---------------------------------------------------------------------------
# File upload settings
# ---------------------------------------------------------------------------

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
