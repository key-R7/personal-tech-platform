from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from social.admin import SocialCommentAdmin, SocialLikeAdmin, SocialPostAdmin
from social.models import SocialComment, SocialLike, SocialPost


class SocialAdminTests(TestCase):
    def test_social_models_are_registered_with_expected_admin_options(self):
        post_admin = admin.site._registry[SocialPost]
        comment_admin = admin.site._registry[SocialComment]
        like_admin = admin.site._registry[SocialLike]

        self.assertIsInstance(post_admin, SocialPostAdmin)
        self.assertIn("feed_type", post_admin.list_filter)
        self.assertIn("author", post_admin.list_filter)
        self.assertIn("content", post_admin.search_fields)
        self.assertIsInstance(comment_admin, SocialCommentAdmin)
        self.assertIn("author", comment_admin.list_filter)
        self.assertIn("content", comment_admin.search_fields)
        self.assertIsInstance(like_admin, SocialLikeAdmin)

    def test_admin_form_rejects_personal_post_by_non_staff_author(self):
        user = get_user_model().objects.create_user(username="ordinary-author")
        post = SocialPost(
            feed_type=SocialPost.FeedType.PERSONAL,
            author=user,
            content="普通用户不能发布到个人主页",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "个人主页动态只能由staff或管理员创建",
        ):
            post.full_clean()


class NavigationTests(TestCase):
    def test_navigation_uses_new_labels_and_named_social_links(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "专业文章")
        self.assertContains(response, "个人项目")
        self.assertContains(response, "社交")
        self.assertContains(
            response,
            f'href="{reverse("social:personal_feed")}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("social:circle_feed")}"',
        )

    def test_existing_article_and_project_urls_remain_unchanged(self):
        self.assertEqual(reverse("blog:article_list"), "/articles/")
        self.assertEqual(reverse("projects:project_list"), "/projects/")
