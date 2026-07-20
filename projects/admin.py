from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "featured",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "featured", "created_at")
    list_editable = ("featured",)
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
