from django.test import TestCase

from projects.models import Project


class ProjectModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title="个人技术平台",
            slug="personal-tech-platform",
            summary="使用Django构建的技术展示平台。",
            description="用于展示文章、项目和个人学习经历。",
            tech_stack="Python、Django、Bootstrap、SQLite",
        )

    def test_string_representation_is_title(self):
        self.assertEqual(str(self.project), self.project.title)

    def test_detail_url_can_be_reversed(self):
        self.assertEqual(
            self.project.get_absolute_url(),
            "/projects/personal-tech-platform/",
        )
