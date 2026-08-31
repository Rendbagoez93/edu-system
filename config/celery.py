import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Create the Celery application — name must match the project for autodiscover
celery_app = Celery("edu_sys")

# Load configuration from Django settings (CELERY_* keys)
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django apps (Celery 5+ requires explicit names)
celery_app.autodiscover_tasks(["core", "academic_structure", "teachers", "students", "schedules", "grade_management", "assessment", "onboarding"])
