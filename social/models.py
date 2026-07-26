from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

IMAGE_MAX_SIZE = 5 * 1024 * 1024
VIDEO_MAX_SIZE = 50 * 1024 * 1024
IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
VIDEO_CONTENT_TYPES = {"video/mp4", "video/webm"}


def social_media_upload_path(filename, media_kind):
    """Return a non-guessable path while retaining the validated extension."""
    extension = Path(filename).suffix.lower()
    created_date = timezone.localdate()
    return (
        f"social/{media_kind}/{created_date:%Y/%m}/"
        f"{uuid4().hex}{extension}"
    )


def social_image_upload_path(instance, filename):
    return social_media_upload_path(filename, "images")


def social_video_upload_path(instance, filename):
    return social_media_upload_path(filename, "videos")


def uploaded_content_type(upload):
    content_type = getattr(upload, "content_type", None)
    if content_type:
        return content_type.lower()
    wrapped_file = getattr(upload, "file", None)
    content_type = getattr(wrapped_file, "content_type", None)
    return content_type.lower() if content_type else None


def validate_image_upload(upload):
    if upload.size > IMAGE_MAX_SIZE:
        raise ValidationError("图片大小不能超过5MB。")
    content_type = uploaded_content_type(upload)
    if content_type and content_type not in IMAGE_CONTENT_TYPES:
        raise ValidationError("图片类型必须是JPEG、PNG或WebP。")


def validate_video_upload(upload):
    if upload.size > VIDEO_MAX_SIZE:
        raise ValidationError("视频大小不能超过50MB。")
    content_type = uploaded_content_type(upload)
    if content_type and content_type not in VIDEO_CONTENT_TYPES:
        raise ValidationError("视频类型必须是MP4或WebM。")


class SocialPost(models.Model):
    class FeedType(models.TextChoices):
        PERSONAL = "personal", "个人主页"
        CIRCLE = "circle", "圈"

    feed_type = models.CharField(
        "动态类型",
        max_length=10,
        choices=FeedType.choices,
        db_index=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        related_name="social_posts",
        on_delete=models.CASCADE,
    )
    content = models.TextField("文字内容", max_length=2000, blank=True)
    image = models.ImageField(
        "图片",
        upload_to=social_image_upload_path,
        blank=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
            validate_image_upload,
        ],
    )
    video = models.FileField(
        "视频",
        upload_to=social_video_upload_path,
        blank=True,
        validators=[
            FileExtensionValidator(["mp4", "webm"]),
            validate_video_upload,
        ],
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "社交动态"
        verbose_name_plural = "社交动态"
        constraints = [
            models.CheckConstraint(
                condition=Q(image="") | Q(video=""),
                name="social_post_single_media",
            ),
            models.CheckConstraint(
                condition=~Q(content="") | ~Q(image="") | ~Q(video=""),
                name="social_post_has_content",
            ),
        ]
        indexes = [
            models.Index(
                fields=["feed_type", "-created_at"],
                name="social_feed_created_idx",
            )
        ]

    def __str__(self):
        return f"{self.get_feed_type_display()} · {self.author} · {self.created_at:%Y-%m-%d}"

    def clean(self):
        super().clean()
        self.content = self.content.strip()
        if not self.content and not self.image and not self.video:
            raise ValidationError("文字、图片和视频至少需要填写一种。")
        if self.image and self.video:
            raise ValidationError("图片和视频不能同时上传。")
        if (
            self.feed_type == self.FeedType.PERSONAL
            and self.author_id
            and not self.author.is_staff
        ):
            raise ValidationError("个人主页动态只能由staff或管理员创建。")

    def get_feed_url(self):
        if self.feed_type == self.FeedType.PERSONAL:
            return reverse("social:personal_feed")
        return reverse("social:circle_feed")


class SocialComment(models.Model):
    post = models.ForeignKey(
        SocialPost,
        verbose_name="动态",
        related_name="comments",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="作者",
        related_name="social_comments",
        on_delete=models.CASCADE,
    )
    content = models.TextField("评论内容", max_length=500)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["created_at", "pk"]
        verbose_name = "社交评论"
        verbose_name_plural = "社交评论"
        indexes = [
            models.Index(
                fields=["post", "created_at"],
                name="social_comment_created_idx",
            )
        ]

    def __str__(self):
        return f"{self.author} 对动态{self.post_id}的评论"

    def clean(self):
        super().clean()
        self.content = self.content.strip()
        if not self.content:
            raise ValidationError({"content": "评论内容不能为空。"})


class SocialLike(models.Model):
    post = models.ForeignKey(
        SocialPost,
        verbose_name="动态",
        related_name="likes",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="用户",
        related_name="social_likes",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "社交点赞"
        verbose_name_plural = "社交点赞"
        constraints = [
            models.UniqueConstraint(
                fields=["post", "user"],
                name="unique_social_like",
            )
        ]

    def __str__(self):
        return f"{self.user} 点赞动态{self.post_id}"
