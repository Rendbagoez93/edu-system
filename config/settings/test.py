"""Test settings — mirrors `local.py` with the shared app enabled.

Referenced by `pyproject.toml`'s `DJANGO_SETTINGS_MODULE = "config.settings.test"`.
See `docs/testing-guide.md` for the full test conventions.
"""

from config.settings.envcommon import env_common
from config.settings.logging import configure_logging

configure_logging(debug=True)

if not env_common.is_local:
    raise RuntimeError(
        "config/settings/test.py is for local tests only. "
        "Use config/settings/local.py or config/settings/production.py for runtime."
    )

SECRET_KEY = env_common.secret_key
DEBUG = True
ALLOWED_HOSTS = env_common.allowed_hosts
BASE_DIR = env_common.base_dir

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "core.User"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "django_celery_beat",
    "apps.shared.apps.SharedConfig",
    "apps.core.apps.CoreConfig",
    "apps.academic_structure.apps.AcademicStructureConfig",
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

LANGUAGE_CODE = "id-ID"
TIME_ZONE = env_common.app_timezone
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
MEDIA_URL = "media/"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@edusys.local"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

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

SPECTACULAR_SETTINGS = {
    "TITLE": env_common.app_name,
    "DESCRIPTION": "School Management System API — tests",
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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Tell pytest-django not to create migrations for the shared app — it has
# no concrete models of its own, only mixins.
MIGRATION_MODULES = {"shared": None}
