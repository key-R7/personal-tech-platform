from django.test import TestCase
from django.utils import timezone

from blog.models import Article, Category, Tag


class TaxonomyModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Python",
            slug="python",
            description="Python相关文章",
        )
        self.first_tag = Tag.objects.create(name="Django", slug="django")
        self.second_tag = Tag.objects.create(name="测试", slug="testing")
        self.article = Article.objects.create(
            title="Django入门",
            slug="django-introduction",
            summary="Django基础知识",
            content="文章正文",
            category=self.category,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_category_string_representation(self):
        self.assertEqual(str(self.category), "Python")

    def test_tag_string_representation(self):
        self.assertEqual(str(self.first_tag), "Django")

    def test_article_can_reference_category(self):
        self.assertEqual(self.article.category, self.category)
        self.assertIn(self.article, self.category.articles.all())

    def test_article_can_reference_multiple_tags(self):
        self.article.tags.add(self.first_tag, self.second_tag)

        self.assertCountEqual(
            self.article.tags.all(),
            [self.first_tag, self.second_tag],
        )

    def test_deleting_category_does_not_delete_article(self):
        article_pk = self.article.pk

        self.category.delete()

        self.assertTrue(Article.objects.filter(pk=article_pk).exists())

    def test_deleting_category_sets_article_category_to_null(self):
        self.category.delete()

        self.article.refresh_from_db()
        self.assertIsNone(self.article.category)

    def test_public_queryset_excludes_drafts_and_articles_without_date(self):
        draft = Article.objects.create(
            title="草稿",
            slug="draft",
            summary="草稿摘要",
            content="草稿正文",
            status=Article.Status.DRAFT,
        )
        without_date = Article.objects.create(
            title="无发布时间",
            slug="without-date",
            summary="无发布时间摘要",
            content="无发布时间正文",
            status=Article.Status.PUBLISHED,
        )

        public_articles = Article.objects.public()

        self.assertIn(self.article, public_articles)
        self.assertNotIn(draft, public_articles)
        self.assertNotIn(without_date, public_articles)
