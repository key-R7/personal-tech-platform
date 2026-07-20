from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article


class ArticleViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.published_article = Article.objects.create(
            title="已发布文章",
            slug="published-article",
            summary="这是一篇已经发布的文章。",
            content="已发布文章正文。",
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.draft_article = Article.objects.create(
            title="草稿文章",
            slug="draft-article",
            summary="这篇文章仍是草稿。",
            content="草稿正文。",
            status=Article.Status.DRAFT,
        )
        cls.unscheduled_article = Article.objects.create(
            title="缺少发布时间的文章",
            slug="article-without-published-at",
            summary="状态已发布，但没有发布时间。",
            content="未设置发布时间的正文。",
            status=Article.Status.PUBLISHED,
            published_at=None,
        )

    def test_article_list_returns_success(self):
        response = self.client.get(reverse("blog:article_list"))

        self.assertEqual(response.status_code, 200)

    def test_published_article_appears_in_list(self):
        response = self.client.get(reverse("blog:article_list"))

        self.assertContains(response, self.published_article.title)

    def test_draft_article_does_not_appear_in_list(self):
        response = self.client.get(reverse("blog:article_list"))

        self.assertNotContains(response, self.draft_article.title)

    def test_article_without_published_at_does_not_appear_in_list(self):
        response = self.client.get(reverse("blog:article_list"))

        self.assertNotContains(response, self.unscheduled_article.title)

    def test_published_article_detail_returns_success(self):
        response = self.client.get(self.published_article.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_article.content)

    def test_draft_article_detail_returns_not_found(self):
        response = self.client.get(self.draft_article.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_article_without_published_at_detail_returns_not_found(self):
        response = self.client.get(self.unscheduled_article.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_unknown_slug_returns_not_found(self):
        response = self.client.get(
            reverse("blog:article_detail", kwargs={"slug": "not-found"})
        )

        self.assertEqual(response.status_code, 404)

    def test_empty_article_list_shows_friendly_message(self):
        Article.objects.all().delete()

        response = self.client.get(reverse("blog:article_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "暂时还没有已发布的文章")

    def test_article_detail_url_can_be_reversed(self):
        url = reverse(
            "blog:article_detail",
            kwargs={"slug": self.published_article.slug},
        )

        self.assertEqual(url, "/articles/published-article/")
