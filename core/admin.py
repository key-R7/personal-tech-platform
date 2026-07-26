from django.contrib import admin

from .models import AboutPageContent, HomePageContent


class SingletonContentAdmin(admin.ModelAdmin):
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not self.model.objects.exists() and super().has_add_permission(
            request
        )


@admin.register(HomePageContent)
class HomePageContentAdmin(SingletonContentAdmin):
    fieldsets = (
        (
            "首页个人介绍",
            {
                "fields": (
                    "role",
                    "direction",
                    "introduction",
                    "career_goal",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(AboutPageContent)
class AboutPageContentAdmin(SingletonContentAdmin):
    fieldsets = (
        (
            "基本介绍",
            {
                "fields": (
                    "role",
                    "direction",
                    "introduction",
                    "education",
                    "education_detail",
                )
            },
        ),
        (
            "学习与能力",
            {
                "fields": (
                    "courses",
                    "experience_highlight",
                    "learning_topics",
                    "skills",
                    "languages",
                    "interests",
                )
            },
        ),
        (
            "目标",
            {
                "fields": (
                    "career_goal",
                    "project_goal",
                    "updated_at",
                )
            },
        ),
    )
