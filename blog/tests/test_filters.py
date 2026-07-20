from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, Category, Tag


class ArticleFilterTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.python = Category.objects.create(name="Python", slug="python")
        cls.web = Category.objects.create(name="Web", slug="web")
        cls.django = Tag.objects.create(name="Django", slug="django")
        cls.testing = Tag.objects.create(name="测试", slug="testing")

        cls.python_article = Article.objects.create(
            title="Learning DJANGO",
            slug="learning-django",
            summary="使用Python构建Web应用",
            content="正文中包含一个只存在于正文的词：repository",
            category=cls.python,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.python_article.tags.add(cls.django)

        cls.web_article = Article.objects.create(
            title="前端基础",
            slug="frontend-basics",
            summary="HTML和CSS学习记录",
            content="前端正文",
            category=cls.web,
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.web_article.tags.add(cls.testing)

        cls.draft = Article.objects.create(
            title="Django草稿",
            slug="django-draft",
            summary="Python草稿摘要",
            content="草稿正文",
            category=cls.python,
            status=Article.Status.DRAFT,
        )
        cls.draft.tags.add(cls.django)

        cls.without_date = Article.objects.create(
            title="Django未正式发布",
            slug="django-without-date",
            summary="Python未发布摘要",
            content="未发布正文",
            category=cls.python,
            status=Article.Status.PUBLISHED,
        )
        cls.without_date.tags.add(cls.django)

    def article_list(self, parameters=None):
        return self.client.get(reverse("blog:article_list"), parameters or {})


class CategoryFilterTests(ArticleFilterTestData):
    def test_category_filter_shows_matching_article(self):
        response = self.article_list({"category": self.python.slug})

        self.assertContains(response, self.python_article.title)

    def test_category_filter_hides_other_category(self):
        response = self.article_list({"category": self.python.slug})

        self.assertNotContains(response, self.web_article.title)

    def test_category_filter_hides_draft(self):
        response = self.article_list({"category": self.python.slug})

        self.assertNotContains(response, self.draft.title)

    def test_category_filter_hides_article_without_published_at(self):
        response = self.article_list({"category": self.python.slug})

        self.assertNotContains(response, self.without_date.title)

    def test_unknown_category_returns_not_found(self):
        response = self.article_list({"category": "not-found"})

        self.assertEqual(response.status_code, 404)


class TagFilterTests(ArticleFilterTestData):
    def test_tag_filter_shows_matching_article(self):
        response = self.article_list({"tag": self.django.slug})

        self.assertContains(response, self.python_article.title)

    def test_tag_filter_hides_article_without_tag(self):
        response = self.article_list({"tag": self.django.slug})

        self.assertNotContains(response, self.web_article.title)

    def test_tag_filter_hides_draft(self):
        response = self.article_list({"tag": self.django.slug})

        self.assertNotContains(response, self.draft.title)

    def test_tag_filter_hides_article_without_published_at(self):
        response = self.article_list({"tag": self.django.slug})

        self.assertNotContains(response, self.without_date.title)

    def test_unknown_tag_returns_not_found(self):
        response = self.article_list({"tag": "not-found"})

        self.assertEqual(response.status_code, 404)


class SearchTests(ArticleFilterTestData):
    def test_searches_title(self):
        response = self.article_list({"q": "Learning"})

        self.assertContains(response, self.python_article.title)

    def test_searches_summary(self):
        response = self.article_list({"q": "HTML"})

        self.assertContains(response, self.web_article.title)

    def test_search_is_case_insensitive(self):
        response = self.article_list({"q": "django"})

        self.assertContains(response, self.python_article.title)

    def test_search_hides_draft(self):
        response = self.article_list({"q": "Django"})

        self.assertNotContains(response, self.draft.title)

    def test_search_hides_article_without_published_at(self):
        response = self.article_list({"q": "Django"})

        self.assertNotContains(response, self.without_date.title)

    def test_no_search_results_returns_success(self):
        response = self.article_list({"q": "不存在的关键词"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "没有找到符合条件的文章")

    def test_blank_search_behaves_like_no_search(self):
        response = self.article_list({"q": "   "})

        self.assertContains(response, self.python_article.title)
        self.assertContains(response, self.web_article.title)

    def test_search_combines_with_category(self):
        response = self.article_list({"q": "Web", "category": "python"})

        self.assertContains(response, self.python_article.title)
        self.assertNotContains(response, self.web_article.title)

    def test_search_combines_with_tag(self):
        response = self.article_list({"q": "Python", "tag": "django"})

        self.assertContains(response, self.python_article.title)
        self.assertNotContains(response, self.web_article.title)

    def test_search_does_not_search_article_content(self):
        response = self.article_list({"q": "repository"})

        self.assertNotContains(response, self.python_article.title)
