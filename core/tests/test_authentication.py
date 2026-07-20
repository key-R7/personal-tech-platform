from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "safe-test-password-123"
        cls.user = get_user_model().objects.create_user(
            username="alice",
            password=cls.password,
        )
        cls.article = Article.objects.create(
            title="认证测试文章",
            slug="authentication-article",
            summary="认证测试摘要",
            content="认证测试正文",
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_login_page_returns_success_and_contains_csrf_token(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_correct_credentials_log_user_in(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("core:home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_incorrect_password_does_not_log_user_in(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.username, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(response, "用户名或密码不正确")

    def test_login_respects_safe_next_parameter(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.username,
                "password": self.password,
                "next": self.article.get_absolute_url(),
            },
        )

        self.assertRedirects(response, self.article.get_absolute_url())

    def test_external_next_parameter_is_not_used(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": self.user.username,
                "password": self.password,
                "next": "https://malicious.example/",
            },
        )

        self.assertRedirects(response, reverse("core:home"))

    def test_logged_in_navigation_shows_username(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, self.user.username)
        self.assertContains(response, reverse("accounts:logout"))

    def test_guest_navigation_shows_login_link(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, reverse("accounts:login"))

    def test_guest_comment_submission_redirects_to_login(self):
        create_url = reverse(
            "blog:comment_create",
            kwargs={"slug": self.article.slug},
        )

        response = self.client.post(create_url, {"content": "游客评论"})

        expected_login_url = f'{reverse("accounts:login")}?next={create_url}'
        self.assertRedirects(response, expected_login_url)

    def test_post_logout_clears_authenticated_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("core:home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_get_logout_is_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)
