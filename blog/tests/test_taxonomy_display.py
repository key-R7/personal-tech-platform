from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, Category, Tag


class ArticleTaxonomyDisplayTests(TestCase):
    def test_detail_displays_linked_category_and_tags(self):
        category = Category.objects.create(name="Python", slug="python")
        tag = Tag.objects.create(name="Django", slug="django")
        article = Article.objects.create(
            title="分类标签文章",
            slug="taxonomy-article",
            summary="摘要",
            content="正文",
            category=category,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        article.tags.add(tag)

        response = self.client.get(article.get_absolute_url())

        self.assertContains(
            response,
            f'{reverse("blog:article_list")}?category={category.slug}',
        )
        self.assertContains(
            response,
            f'{reverse("blog:article_list")}?tag={tag.slug}',
        )

    def test_detail_without_category_or_tags_returns_success(self):
        article = Article.objects.create(
            title="无分类标签文章",
            slug="article-without-taxonomy",
            summary="摘要",
            content="正文",
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        response = self.client.get(article.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
