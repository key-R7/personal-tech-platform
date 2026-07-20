"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("core.auth_urls")),
    path("articles/", include("blog.urls")),
    path("projects/", include("projects.urls")),
    path("", include("core.urls")),
]
