from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apis.v1.core.urls")),
    path("api/v1/", include("apis.v1.academic_structure.urls")),
    path("api/v1/", include("apis.v1.teachers.urls")),
    path("api/v1/", include("apis.v1.students.urls")),
    # Web page routes
    path("", include("apps.core.urls")),
]
