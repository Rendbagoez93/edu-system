"""
Settings package — auto-selects local.py or production.py based on ENVIRONMENT.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings   # auto-selects based on .env

Or use the specific module directly:
    DJANGO_SETTINGS_MODULE=config.settings.local
    DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os

# Check ENVIRONMENT directly from the OS — pydantic-settings will handle
# loading .env when the actual settings module (local.py / production.py) starts.
_environment = os.environ.get("ENVIRONMENT", "local")

if _environment == "prod":
    from config.settings.production import *  # noqa: F401, F403, E402
else:
    from config.settings.local import *  # noqa: F401, F403, E402
