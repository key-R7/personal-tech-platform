from django.contrib import admin

from .models import SocialComment, SocialLike, SocialPost


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ("feed_type", "author", "content_preview", "created_at")
    list_filter = ("feed_type", "author", "created_at")
    search_fields = ("content", "author__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("author",)

    @admin.display(description="内容")
    def content_preview(self, post):
        return post.content[:60] or "（仅媒体）"


@admin.register(SocialComment)
class SocialCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "content_preview", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("content", "author__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("post", "author")

    @admin.display(description="内容")
    def content_preview(self, comment):
        return comment.content[:60]


@admin.register(SocialLike)
class SocialLikeAdmin(admin.ModelAdmin):
    list_display = ("post", "user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__content")
    readonly_fields = ("post", "user", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
