from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from core.admin import AboutPageContentAdmin, HomePageContentAdmin
from core.context_processors import SITE_PROFILE
from core.models import AboutPageContent, HomePageContent


class EditablePageContentTests(TestCase):
    def setUp(self):
        self.home_content = HomePageContent.objects.get(singleton_key=1)
        self.about_content = AboutPageContent.objects.get(singleton_key=1)

    def test_migration_preserves_verified_personal_content(self):
        self.assertEqual(self.home_content.role, SITE_PROFILE["role"])
        self.assertEqual(self.about_content.education, SITE_PROFILE["education"])
        self.assertIn("CET-6", self.about_content.languages)

    def test_home_uses_database_content_after_admin_style_update(self):
        self.home_content.role = "可编辑的首页定位"
        self.home_content.introduction = "可编辑的首页简介"
        self.home_content.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "可编辑的首页定位")
        self.assertContains(response, "可编辑的首页简介")
        self.assertNotContains(response, SITE_PROFILE["role"])

    def test_about_uses_database_content_and_newline_lists(self):
        self.about_content.education = "可编辑教育背景"
        self.about_content.learning_topics = "第一项学习方向\n第二项学习方向"
        self.about_content.save()

        response = self.client.get(reverse("core:about"))

        self.assertContains(response, "可编辑教育背景")
        self.assertContains(response, "<li>第一项学习方向</li>", html=True)
        self.assertContains(response, "<li>第二项学习方向</li>", html=True)

    def test_home_falls_back_to_verified_content_without_record(self):
        HomePageContent.objects.all().delete()

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, SITE_PROFILE["role"])
        self.assertContains(response, SITE_PROFILE["introduction"])

    def test_about_falls_back_to_verified_content_without_record(self):
        AboutPageContent.objects.all().delete()

        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, SITE_PROFILE["education"])
        self.assertContains(response, SITE_PROFILE["skills"][0])

    def test_page_content_remains_template_escaped(self):
        self.home_content.introduction = "<script>alert('profile')</script>"
        self.home_content.save()

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "&lt;script&gt;", html=False)
        self.assertNotContains(
            response,
            "<script>alert('profile')</script>",
            html=False,
        )

    def test_singleton_models_reject_duplicate_records(self):
        duplicate = HomePageContent(
            role="重复",
            direction="重复",
            introduction="重复",
            career_goal="重复",
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class EditableContentAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.superuser = User.objects.create_superuser(
            username="content-admin",
            password="temporary-test-password",
        )
        cls.ordinary_user = User.objects.create_user(username="ordinary-user")

    def test_models_are_registered_in_admin(self):
        self.assertIsInstance(
            admin.site._registry[HomePageContent],
            HomePageContentAdmin,
        )
        self.assertIsInstance(
            admin.site._registry[AboutPageContent],
            AboutPageContentAdmin,
        )

    def test_admin_does_not_offer_duplicate_add_when_content_exists(self):
        request = RequestFactory().get("/admin/")
        request.user = self.superuser

        self.assertFalse(
            admin.site._registry[HomePageContent].has_add_permission(request)
        )
        self.assertFalse(
            admin.site._registry[AboutPageContent].has_add_permission(request)
        )

    def test_ordinary_user_cannot_access_content_admin(self):
        self.client.force_login(self.ordinary_user)

        response = self.client.get(
            reverse("admin:core_homepagecontent_changelist")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)

    def test_superuser_can_update_home_content_through_admin(self):
        content = HomePageContent.objects.get(singleton_key=1)
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse(
                "admin:core_homepagecontent_change",
                kwargs={"object_id": content.pk},
            ),
            {
                "role": "Admin更新后的定位",
                "direction": content.direction,
                "introduction": content.introduction,
                "career_goal": content.career_goal,
                "_save": "保存",
            },
        )

        self.assertEqual(response.status_code, 302)
        content.refresh_from_db()
        self.assertEqual(content.role, "Admin更新后的定位")
