from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment_delete"),
    path("<slug:slug>/comments/create/", views.comment_create, name="comment_create"),
    path("<slug:slug>/", views.article_detail, name="article_detail"),
]
