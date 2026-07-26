from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from social.models import SocialComment, SocialLike, SocialPost


class SocialInteractionTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create_user(username="interaction-author")
        cls.other_user = User.objects.create_user(username="interaction-other")
        cls.staff = User.objects.create_user(
            username="interaction-staff",
            is_staff=True,
        )
        cls.post = SocialPost.objects.create(
            feed_type=SocialPost.FeedType.CIRCLE,
            author=cls.author,
            content="用于互动的动态",
        )
        cls.other_post = SocialPost.objects.create(
            feed_type=SocialPost.FeedType.CIRCLE,
            author=cls.other_user,
            content="另一条动态",
        )

    def comment_url(self, post=None):
        return reverse(
            "social:comment_create",
            kwargs={"post_id": (post or self.post).pk},
        )

    def like_url(self, post=None):
        return reverse(
            "social:like_toggle",
            kwargs={"post_id": (post or self.post).pk},
        )


class SocialCommentViewTests(SocialInteractionTestData):
    def test_logged_in_user_can_comment_and_author_is_server_controlled(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            self.comment_url(),
            {"content": "有效评论", "author": self.author.pk},
        )

        comment = SocialComment.objects.get()
        self.assertEqual(comment.author, self.other_user)
        self.assertEqual(comment.post, self.post)
        self.assertRedirects(response, reverse("social:circle_feed"))

    def test_guest_cannot_comment(self):
        response = self.client.post(
            self.comment_url(),
            {"content": "游客评论"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialComment.objects.exists())

    def test_empty_and_overlong_comments_are_not_saved(self):
        self.client.force_login(self.author)

        self.client.post(self.comment_url(), {"content": "   "})
        self.client.post(self.comment_url(), {"content": "a" * 501})

        self.assertFalse(SocialComment.objects.exists())

    def test_comment_author_can_delete_own_comment(self):
        comment = SocialComment.objects.create(
            post=self.post,
            author=self.author,
            content="待删除评论",
        )
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("social:comment_delete", kwargs={"comment_id": comment.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialComment.objects.filter(pk=comment.pk).exists())

    def test_other_user_cannot_delete_comment(self):
        comment = SocialComment.objects.create(
            post=self.post,
            author=self.author,
            content="不能越权删除",
        )
        self.client.force_login(self.other_user)

        with self.assertLogs("social.views", level="WARNING"):
            response = self.client.post(
                reverse(
                    "social:comment_delete",
                    kwargs={"comment_id": comment.pk},
                )
            )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(SocialComment.objects.filter(pk=comment.pk).exists())

    def test_staff_can_delete_any_comment(self):
        comment = SocialComment.objects.create(
            post=self.post,
            author=self.author,
            content="管理员可删除",
        )
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("social:comment_delete", kwargs={"comment_id": comment.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialComment.objects.filter(pk=comment.pk).exists())

    def test_get_cannot_create_or_delete_comment(self):
        comment = SocialComment.objects.create(
            post=self.post,
            author=self.author,
            content="GET不能删除",
        )
        self.client.force_login(self.author)

        create_response = self.client.get(self.comment_url())
        delete_response = self.client.get(
            reverse("social:comment_delete", kwargs={"comment_id": comment.pk})
        )

        self.assertEqual(create_response.status_code, 405)
        self.assertEqual(delete_response.status_code, 405)
        self.assertTrue(SocialComment.objects.filter(pk=comment.pk).exists())

    def test_comment_content_is_template_escaped(self):
        SocialComment.objects.create(
            post=self.post,
            author=self.author,
            content="<script>alert('social')</script>",
        )

        response = self.client.get(reverse("social:circle_feed"))

        self.assertContains(response, "&lt;script&gt;", html=False)
        self.assertNotContains(
            response,
            "<script>alert('social')</script>",
            html=False,
        )

    def test_comment_post_requires_csrf(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.author)

        response = csrf_client.post(
            self.comment_url(),
            {"content": "无CSRF"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(SocialComment.objects.exists())


class SocialLikeViewTests(SocialInteractionTestData):
    def test_logged_in_user_can_like_and_click_again_to_unlike(self):
        self.client.force_login(self.author)

        first_response = self.client.post(self.like_url())
        self.assertEqual(first_response.status_code, 302)
        self.assertEqual(SocialLike.objects.count(), 1)

        second_response = self.client.post(self.like_url())
        self.assertEqual(second_response.status_code, 302)
        self.assertEqual(SocialLike.objects.count(), 0)

    def test_guest_cannot_like(self):
        response = self.client.post(self.like_url())

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialLike.objects.exists())

    def test_liking_different_posts_does_not_interfere(self):
        self.client.force_login(self.author)

        self.client.post(self.like_url(self.post))
        self.client.post(self.like_url(self.other_post))

        self.assertEqual(SocialLike.objects.count(), 2)

    def test_get_does_not_change_like_state(self):
        self.client.force_login(self.author)

        response = self.client.get(self.like_url())

        self.assertEqual(response.status_code, 405)
        self.assertFalse(SocialLike.objects.exists())

    def test_feed_marks_current_users_like_without_hiding_counts(self):
        SocialLike.objects.create(post=self.post, user=self.author)
        SocialLike.objects.create(post=self.post, user=self.other_user)
        self.client.force_login(self.author)

        response = self.client.get(reverse("social:circle_feed"))
        rendered_post = next(
            post
            for post in response.context["posts"]
            if post.pk == self.post.pk
        )

        self.assertTrue(rendered_post.user_has_liked)
        self.assertEqual(rendered_post.like_count, 2)
        self.assertContains(response, "取消点赞")

    def test_logged_in_user_can_like_and_comment_on_personal_post(self):
        personal_post = SocialPost.objects.create(
            feed_type=SocialPost.FeedType.PERSONAL,
            author=self.staff,
            content="可互动的个人主页动态",
        )
        self.client.force_login(self.author)

        self.client.post(self.like_url(personal_post))
        self.client.post(
            self.comment_url(personal_post),
            {"content": "个人主页评论"},
        )

        self.assertTrue(
            SocialLike.objects.filter(
                post=personal_post,
                user=self.author,
            ).exists()
        )
        self.assertTrue(
            SocialComment.objects.filter(
                post=personal_post,
                author=self.author,
            ).exists()
        )


class SocialPostDeleteTests(SocialInteractionTestData):
    def test_author_can_delete_own_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("social:post_delete", kwargs={"post_id": self.post.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialPost.objects.filter(pk=self.post.pk).exists())

    def test_other_user_cannot_delete_post(self):
        self.client.force_login(self.other_user)

        with self.assertLogs("social.views", level="WARNING"):
            response = self.client.post(
                reverse(
                    "social:post_delete",
                    kwargs={"post_id": self.post.pk},
                )
            )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(SocialPost.objects.filter(pk=self.post.pk).exists())

    def test_staff_can_delete_any_post(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("social:post_delete", kwargs={"post_id": self.post.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialPost.objects.filter(pk=self.post.pk).exists())

    def test_get_displays_confirmation_without_deleting_post(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("social:post_delete", kwargs={"post_id": self.post.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "确认删除动态")
        self.assertContains(response, self.post.content)
        self.assertTrue(SocialPost.objects.filter(pk=self.post.pk).exists())

    def test_delete_confirmation_posts_to_same_named_url(self):
        self.client.force_login(self.author)
        delete_url = reverse(
            "social:post_delete",
            kwargs={"post_id": self.post.pk},
        )

        response = self.client.get(delete_url)

        self.assertContains(response, f'action="{delete_url}"')
        self.assertContains(response, 'type="submit">确认删除')

    def test_unknown_resources_return_not_found(self):
        self.client.force_login(self.author)

        self.assertEqual(
            self.client.post(
                reverse("social:like_toggle", kwargs={"post_id": 999999})
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse("social:post_delete", kwargs={"post_id": 999999})
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse(
                    "social:comment_delete",
                    kwargs={"comment_id": 999999},
                )
            ).status_code,
            404,
        )
