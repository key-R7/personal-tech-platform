from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from blog.models import Article, Category, Tag
from projects.models import Project


class SeedDemoCommandTests(TestCase):
    def setUp(self):
        Project.objects.all().delete()

    def run_command(self):
        output = StringIO()
        call_command("seed_demo", stdout=output)
        return output.getvalue()

    def test_command_creates_labeled_demo_content(self):
        output = self.run_command()

        self.assertIn("演示数据准备完成", output)
        self.assertEqual(Article.objects.count(), 4)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Tag.objects.count(), 5)
        self.assertEqual(Project.objects.count(), 3)
        self.assertFalse(
            Article.objects.exclude(title__startswith="[演示]").exists()
        )
        self.assertFalse(
            Project.objects.exclude(title__startswith="[演示]").exists()
        )
        self.assertEqual(Article.objects.public().count(), 4)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_command_is_idempotent(self):
        self.run_command()
        self.run_command()

        self.assertEqual(Article.objects.count(), 4)
        self.assertEqual(Category.objects.count(), 2)
        self.assertEqual(Tag.objects.count(), 5)
        self.assertEqual(Project.objects.count(), 3)

    def test_command_does_not_overwrite_existing_slug(self):
        project = Project.objects.create(
            title="用户已有项目",
            slug="demo-django-content-platform",
            summary="保留此内容",
            description="保留此详情",
            tech_stack="Python",
        )

        self.run_command()
        project.refresh_from_db()

        self.assertEqual(project.title, "用户已有项目")
        self.assertEqual(project.summary, "保留此内容")
