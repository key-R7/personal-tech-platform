from django.test import TestCase

from projects.models import Project


class InitialPortfolioProjectTests(TestCase):
    def test_immersive_resume_project_is_available(self):
        project = Project.objects.get(slug="immersive-ai-resume")

        self.assertEqual(project.title, "3D 双语个人简历网站")
        self.assertEqual(project.status, Project.Status.DEVELOPING)
        self.assertTrue(project.featured)
        self.assertEqual(project.github_url, "")
        self.assertEqual(project.demo_url, "")
        self.assertIn("Next.js", project.tech_stack)
        self.assertIn("尚未建立公开 Git 仓库", project.description)

    def test_immersive_resume_project_detail_page_is_public(self):
        project = Project.objects.get(slug="immersive-ai-resume")

        response = self.client.get(project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, project.title)
        self.assertContains(response, "React Three Fiber")
        self.assertNotContains(response, "查看GitHub")
        self.assertNotContains(response, ">在线演示</a>", html=False)
