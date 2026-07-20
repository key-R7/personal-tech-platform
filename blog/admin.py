from django.contrib import admin

from .models import Article, Category, Comment, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name", "slug")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    ordering = ("name", "slug")
    readonly_fields = ("created_at",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "created_at",
        "published_at",
    )
    list_filter = (
        "status",
        "category",
        "tags",
        "created_at",
        "published_at",
    )
    search_fields = ("title",)
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("article", "author", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("content", "author__username", "article__title")
    readonly_fields = ("created_at", "updated_at")
