from config.settings.databases import db_settings
from config.settings.envcommon import env_common
from config.settings.logging import configure_logging

# Activate logging first
configure_logging(debug=True)

# ---------------------------------------------------------------------------
# Environment guard — this file is only for local use
# ---------------------------------------------------------------------------

if not env_common.is_local:
    raise RuntimeError(
        "config/settings/local.py is for local development only. "
        "Use config/settings/production.py for production deployments."
    )

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

SECRET_KEY = env_common.secret_key
DEBUG = True
ALLOWED_HOSTS = env_common.allowed_hosts
BASE_DIR = env_common.base_dir

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# AUTH_USER_MODEL = "core.User"  # uncomment once core.User is defined

# ---------------------------------------------------------------------------
# Database — SQLite (see databases.py)
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": db_settings.sqlite_name,
        "ATOMIC_REQUESTS": False,
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
    # # Layer 0 — Foundation
    # "core.apps.CoreConfig",
    # "shared.apps.SharedConfig",
    # # Layer 1 — Structure
    # "academic_structure.apps.AcademicStructureConfig",
    # # Layer 2 — Entities
    # "teachers.apps.TeachersConfig",
    # "students.apps.StudentsConfig",
    # # Layer 3 — Scheduling
    # "schedules.apps.SchedulesConfig",
    # # Layer 4 — Assignment
    # "grade_management.apps.GradeManagementConfig",
    # # Layer 5 — Scoring
    # "assessment.apps.AssessmentConfig",
    # # Orchestrator
    # "onboarding.apps.OnboardingConfig",
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
# Email — console backend for local dev
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@edusys.local"

# ---------------------------------------------------------------------------
# Caches — dummy cache for local dev (no Redis required)
# ---------------------------------------------------------------------------

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# ---------------------------------------------------------------------------
# Celery — eager mode: tasks run synchronously, no broker needed
# ---------------------------------------------------------------------------

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

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
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# drf-spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": env_common.app_name,
    "DESCRIPTION": "School Management System API — local development",
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
# Security — relaxed for local dev
# ---------------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = "SAMEORIGIN"

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
