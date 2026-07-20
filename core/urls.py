from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("favicon.ico", views.favicon, name="favicon"),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
]
