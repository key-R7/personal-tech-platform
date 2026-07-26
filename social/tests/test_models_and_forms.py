from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, UploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from social.forms import CirclePostForm, SocialCommentForm
from social.models import SocialComment, SocialLike, SocialPost


def valid_png(name="test.png"):
    image_bytes = BytesIO()
    Image.new("RGB", (2, 2), color="blue").save(image_bytes, format="PNG")
    return SimpleUploadedFile(
        name,
        image_bytes.getvalue(),
        content_type="image/png",
    )


def valid_video(name="test.mp4"):
    return SimpleUploadedFile(name, b"test-video", content_type="video/mp4")


class SocialModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="social-user")
        cls.other_user = User.objects.create_user(username="other-social-user")
        cls.staff = User.objects.create_user(
            username="social-staff",
            is_staff=True,
        )

    def post(self, **overrides):
        values = {
            "feed_type": SocialPost.FeedType.CIRCLE,
            "author": self.user,
            "content": "测试动态",
        }
        values.update(overrides)
        return SocialPost(**values)

    def test_personal_post_requires_staff_author(self):
        post = self.post(feed_type=SocialPost.FeedType.PERSONAL)

        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_staff_can_create_personal_post(self):
        post = self.post(
            feed_type=SocialPost.FeedType.PERSONAL,
            author=self.staff,
        )

        post.full_clean()
        post.save()

        self.assertEqual(post.get_feed_url(), "/social/personal/")

    def test_circle_post_uses_circle_feed_url(self):
        post = self.post()
        post.full_clean()
        post.save()

        self.assertEqual(post.get_feed_url(), "/social/circle/")

    def test_post_rejects_empty_content_and_media(self):
        with self.assertRaises(ValidationError):
            self.post(content=" \n ").full_clean()

    def test_post_rejects_image_and_video_together(self):
        with self.assertRaises(ValidationError):
            self.post(
                content="",
                image=valid_png(),
                video=valid_video(),
            ).full_clean()

    def test_comment_rejects_whitespace_only_content(self):
        post = self.post()
        post.full_clean()
        post.save()
        comment = SocialComment(post=post, author=self.user, content=" \n ")

        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_deleting_post_cascades_comments_and_likes(self):
        post = self.post()
        post.full_clean()
        post.save()
        SocialComment.objects.create(
            post=post,
            author=self.user,
            content="评论",
        )
        SocialLike.objects.create(post=post, user=self.user)

        post.delete()

        self.assertFalse(SocialComment.objects.exists())
        self.assertFalse(SocialLike.objects.exists())

    def test_database_constraint_prevents_duplicate_like(self):
        post = self.post()
        post.full_clean()
        post.save()
        SocialLike.objects.create(post=post, user=self.user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            SocialLike.objects.create(post=post, user=self.user)


class SocialUploadFormTests(TestCase):
    def setUp(self):
        self.media_directory = TemporaryDirectory()
        self.override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        self.media_directory.cleanup()

    def test_valid_image_is_accepted(self):
        form = CirclePostForm(
            {"content": ""},
            {"image": valid_png()},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_video_is_accepted(self):
        form = CirclePostForm(
            {"content": ""},
            {"video": valid_video()},
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_image_and_video_cannot_be_uploaded_together(self):
        form = CirclePostForm(
            {"content": "包含两个文件"},
            {"image": valid_png(), "video": valid_video()},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("图片和视频不能同时上传", str(form.non_field_errors()))

    def test_disallowed_image_extension_is_rejected(self):
        form = CirclePostForm(
            {"content": ""},
            {
                "image": SimpleUploadedFile(
                    "image.gif",
                    b"GIF89a",
                    content_type="image/gif",
                )
            },
        )

        self.assertFalse(form.is_valid())

    def test_oversized_video_is_rejected_without_allocating_50mb(self):
        upload = UploadedFile(
            file=BytesIO(b"x"),
            name="large.mp4",
            content_type="video/mp4",
            size=50 * 1024 * 1024 + 1,
        )
        form = CirclePostForm({"content": ""}, {"video": upload})

        self.assertFalse(form.is_valid())
        self.assertIn("视频大小不能超过50MB", str(form.errors))

    def test_oversized_image_is_rejected_without_allocating_5mb(self):
        image = valid_png()
        upload = UploadedFile(
            file=BytesIO(image.read()),
            name="large.png",
            content_type="image/png",
            size=5 * 1024 * 1024 + 1,
        )
        form = CirclePostForm({"content": ""}, {"image": upload})

        self.assertFalse(form.is_valid())
        self.assertIn("图片大小不能超过5MB", str(form.errors))

    def test_allowed_extension_with_wrong_video_mime_is_rejected(self):
        form = CirclePostForm(
            {"content": ""},
            {
                "video": SimpleUploadedFile(
                    "fake.mp4",
                    b"not-a-video",
                    content_type="application/octet-stream",
                )
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("视频类型必须是MP4或WebM", str(form.errors))

    def test_empty_post_is_rejected(self):
        form = CirclePostForm({"content": "   "})

        self.assertFalse(form.is_valid())
        self.assertIn("至少需要填写一种", str(form.non_field_errors()))

    def test_comment_form_rejects_empty_and_overlong_content(self):
        self.assertFalse(SocialCommentForm({"content": "   "}).is_valid())
        self.assertFalse(SocialCommentForm({"content": "a" * 501}).is_valid())

    def test_uploaded_files_receive_unique_non_original_names(self):
        User = get_user_model()
        user = User.objects.create_user(username="upload-user")
        first = SocialPost(
            feed_type=SocialPost.FeedType.CIRCLE,
            author=user,
            image=valid_png("same-name.png"),
        )
        first.full_clean()
        first.save()
        second = SocialPost(
            feed_type=SocialPost.FeedType.CIRCLE,
            author=user,
            image=valid_png("same-name.png"),
        )
        second.full_clean()
        second.save()

        self.assertNotEqual(first.image.name, second.image.name)
        self.assertNotIn("same-name", first.image.name)
        self.assertTrue(Path(first.image.path).exists())
        self.assertTrue(first.image.url.startswith("/media/social/images/"))
