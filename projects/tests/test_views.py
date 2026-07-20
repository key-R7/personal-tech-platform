from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from projects.admin import ProjectAdmin
from projects.models import Project


class ProjectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title="示例项目",
            slug="example-project",
            summary="项目简介",
            description="项目详细介绍",
            tech_stack="Python、Django",
            github_url="https://github.com/example/example-project",
            demo_url="https://example.com",
            status=Project.Status.MAINTAINING,
            featured=True,
        )

    def test_project_list_returns_success(self):
        response = self.client.get(reverse("projects:project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/project_list.html")
        self.assertContains(response, self.project.title)

    def test_project_detail_returns_success(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/project_detail.html")
        self.assertContains(response, self.project.description)

    def test_unknown_slug_returns_not_found(self):
        response = self.client.get(
            reverse("projects:project_detail", kwargs={"slug": "not-found"})
        )

        self.assertEqual(response.status_code, 404)

    def test_empty_project_list_shows_friendly_message(self):
        Project.objects.all().delete()

        response = self.client.get(reverse("projects:project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "暂时还没有可展示的项目")

    def test_detail_shows_external_links_with_safe_attributes(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertInHTML(
            (
                '<a class="btn btn-outline-info" '
                f'href="{self.project.github_url}" target="_blank" '
                'rel="noopener noreferrer">查看GitHub</a>'
            ),
            response.content.decode(),
        )
        self.assertInHTML(
            (
                '<a class="btn btn-info" '
                f'href="{self.project.demo_url}" target="_blank" '
                'rel="noopener noreferrer">在线演示</a>'
            ),
            response.content.decode(),
        )

    def test_detail_hides_empty_external_links(self):
        project = Project.objects.create(
            title="无外链项目",
            slug="project-without-links",
            summary="没有外部链接",
            description="详情",
            tech_stack="Python",
        )

        response = self.client.get(project.get_absolute_url())

        self.assertNotContains(response, "查看GitHub")
        self.assertNotContains(response, "在线演示")

    def test_project_is_registered_with_expected_admin_options(self):
        project_admin = admin.site._registry[Project]

        self.assertIsInstance(project_admin, ProjectAdmin)
        self.assertIn("title", project_admin.search_fields)
        self.assertIn("status", project_admin.list_filter)
        self.assertIn("featured", project_admin.list_filter)
        self.assertIn("featured", project_admin.list_editable)
