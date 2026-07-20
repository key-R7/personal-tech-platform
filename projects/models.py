from django.db import models
from django.urls import reverse


class Project(models.Model):
    class Status(models.TextChoices):
        DEVELOPING = "developing", "开发中"
        COMPLETED = "completed", "已完成"
        MAINTAINING = "maintaining", "维护中"

    title = models.CharField("项目名称", max_length=200)
    slug = models.SlugField(
        "URL 标识",
        max_length=200,
        unique=True,
        help_text="用于项目详情页地址，请使用英文字母、数字、连字符或下划线。",
    )
    summary = models.CharField("项目简介", max_length=500)
    description = models.TextField("详细介绍")
    tech_stack = models.TextField(
        "技术栈",
        help_text="简要说明项目使用的语言、框架和工具。",
    )
    github_url = models.URLField("GitHub 地址", blank=True)
    demo_url = models.URLField("在线演示地址", blank=True)
    status = models.CharField(
        "项目状态",
        max_length=12,
        choices=Status.choices,
        default=Status.DEVELOPING,
        db_index=True,
    )
    featured = models.BooleanField("精选项目", default=False, db_index=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-featured", "-updated_at", "-created_at"]
        verbose_name = "项目"
        verbose_name_plural = "项目"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("projects:project_detail", kwargs={"slug": self.slug})
