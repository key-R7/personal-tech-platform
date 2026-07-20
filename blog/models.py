from django.conf import settings
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("分类名称", max_length=100)
    slug = models.SlugField(
        "URL 标识",
        max_length=100,
        unique=True,
        help_text="由管理员填写，用于文章列表的分类筛选。",
    )
    description = models.TextField("分类说明", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["name", "slug"]
        verbose_name = "文章分类"
        verbose_name_plural = "文章分类"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("标签名称", max_length=50)
    slug = models.SlugField(
        "URL 标识",
        max_length=50,
        unique=True,
        help_text="由管理员填写，用于文章列表的标签筛选。",
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["name", "slug"]
        verbose_name = "文章标签"
        verbose_name_plural = "文章标签"

    def __str__(self):
        return self.name


class ArticleQuerySet(models.QuerySet):
    def public(self):
        """Return articles that visitors are allowed to read."""
        return self.filter(
            status=Article.Status.PUBLISHED,
            published_at__isnull=False,
        )


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    title = models.CharField("标题", max_length=200)
    slug = models.SlugField(
        "URL 标识",
        max_length=200,
        unique=True,
        help_text="用于文章详情页地址，请使用英文字母、数字、连字符或下划线。",
    )
    summary = models.CharField("摘要", max_length=500)
    content = models.TextField("正文")
    category = models.ForeignKey(
        Category,
        verbose_name="分类",
        related_name="articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="标签",
        related_name="articles",
        blank=True,
    )
    status = models.CharField(
        "状态",
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    published_at = models.DateTimeField("发布时间", null=True, blank=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog:article_detail", kwargs={"slug": self.slug})


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        verbose_name="文章",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        related_name="article_comments",
        on_delete=models.CASCADE,
    )
    content = models.TextField("评论内容", max_length=500)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "文章评论"
        verbose_name_plural = "文章评论"
        indexes = [
            models.Index(
                fields=["article", "created_at"],
                name="comment_article_created_idx",
            )
        ]

    def __str__(self):
        return f"{self.author} 对《{self.article}》的评论"
