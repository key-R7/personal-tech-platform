from django.urls import path

from . import views

app_name = "social"

urlpatterns = [
    path("personal/", views.personal_feed, name="personal_feed"),
    path("circle/", views.circle_feed, name="circle_feed"),
    path("posts/<int:post_id>/like/", views.like_toggle, name="like_toggle"),
    path("posts/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path(
        "posts/<int:post_id>/comments/create/",
        views.comment_create,
        name="comment_create",
    ),
    path(
        "comments/<int:comment_id>/delete/",
        views.comment_delete,
        name="comment_delete",
    ),
]
