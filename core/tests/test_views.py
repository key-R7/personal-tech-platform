from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article
from projects.models import Project


class HomeViewTests(TestCase):
    def setUp(self):
        Project.objects.all().delete()

    def create_article(
        self,
        number,
        *,
        status=Article.Status.PUBLISHED,
        published_at=None,
    ):
        if published_at is None and status == Article.Status.PUBLISHED:
            published_at = timezone.now() + timedelta(minutes=number)
        return Article.objects.create(
            title=f"文章{number}",
            slug=f"article-{number}",
            summary=f"文章{number}的摘要",
            content=f"文章{number}的正文",
            status=status,
            published_at=published_at,
        )

    def create_project(self, number, *, featured):
        project = Project.objects.create(
            title=f"项目{number}",
            slug=f"project-{number}",
            summary=f"项目{number}的简介",
            description=f"项目{number}的详细介绍",
            tech_stack="Python、Django",
            featured=featured,
        )
        Project.objects.filter(pk=project.pk).update(
            updated_at=timezone.now() + timedelta(minutes=number)
        )
        project.refresh_from_db()
        return project

    def test_home_page_returns_success(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_starts_with_split_text_intro(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, 'aria-label="This is key !"')
        self.assertContains(response, 'href="#profile-introduction"')
        self.assertContains(response, 'id="profile-introduction"')
        self.assertContains(response, 'rel="stylesheet"')
        self.assertContains(response, "?v=20260724-2")
        self.assertContains(response, "css/editorial")
        self.assertContains(response, "js/site")

    def test_home_uses_split_showcases_for_articles_and_projects(self):
        self.create_article(1)
        self.create_project(1, featured=True)

        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.content.count(b"data-split-showcase"), 2)
        self.assertContains(response, "split-card-tone-0")

    def test_home_shows_at_most_three_recent_articles(self):
        articles = [self.create_article(number) for number in range(4)]

        response = self.client.get(reverse("core:home"))

        recent_articles = list(response.context["recent_articles"])
        self.assertEqual(len(recent_articles), 3)
        self.assertEqual(
            [article.pk for article in recent_articles],
            [article.pk for article in reversed(articles[1:])],
        )

    def test_home_does_not_show_draft_article(self):
        draft = self.create_article(1, status=Article.Status.DRAFT)

        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, draft.title)

    def test_home_does_not_show_article_without_published_at(self):
        article = self.create_article(1)
        Article.objects.filter(pk=article.pk).update(published_at=None)

        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, article.title)

    def test_home_only_shows_featured_projects(self):
        featured = self.create_project(1, featured=True)
        regular = self.create_project(2, featured=False)

        response = self.client.get(reverse("core:home"))

        self.assertContains(response, featured.title)
        self.assertNotContains(response, regular.title)

    def test_home_shows_at_most_three_featured_projects(self):
        projects = [
            self.create_project(number, featured=True) for number in range(4)
        ]

        response = self.client.get(reverse("core:home"))

        featured_projects = list(response.context["featured_projects"])
        self.assertEqual(len(featured_projects), 3)
        self.assertEqual(
            [project.pk for project in featured_projects],
            [project.pk for project in reversed(projects[1:])],
        )

    def test_home_handles_empty_articles_and_projects(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "暂时还没有已发布的文章")
        self.assertContains(response, "暂时还没有精选项目")


class AboutAndNavigationTests(TestCase):
    def test_about_page_returns_success(self):
        response = self.client.get(reverse("core:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/about.html")

    def test_home_contains_article_navigation_link(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, f'href="{reverse("blog:article_list")}"')

    def test_home_contains_project_navigation_link(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, f'href="{reverse("projects:project_list")}"')

    def test_home_contains_about_navigation_link(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, f'href="{reverse("core:about")}"')

    def test_named_internal_routes_resolve_and_return_success(self):
        expected_urls = {
            "core:home": "/",
            "core:about": "/about/",
            "blog:article_list": "/articles/",
            "projects:project_list": "/projects/",
        }

        for route_name, expected_url in expected_urls.items():
            with self.subTest(route_name=route_name):
                url = reverse(route_name)
                self.assertEqual(url, expected_url)
                self.assertEqual(self.client.get(url).status_code, 200)


class ProfileContentTests(TestCase):
    def test_home_displays_verified_resume_profile(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, "吴柯毅")
        self.assertContains(response, "后端开发")
        self.assertContains(response, "东北林业大学")
        self.assertContains(response, "15840486398@163.com")

    def test_about_displays_education_skills_and_languages(self):
        response = self.client.get(reverse("core:about"))

        self.assertContains(response, "2024年9月至今")
        self.assertContains(response, "多Agent协作工作流")
        self.assertContains(response, "CET-4、CET-6均通过")
        self.assertContains(response, "英文文献批量整理工作压缩至15分钟")

    def test_missing_github_url_does_not_render_placeholder_link(self):
        response = self.client.get(reverse("core:home"))

        self.assertNotContains(response, "GitHub（待填写）")
