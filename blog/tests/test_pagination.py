from datetime import timedelta
from urllib.parse import parse_qs

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, Category, Tag


class ArticlePaginationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Python", slug="python")
        cls.tag = Tag.objects.create(name="Django", slug="django")
        cls.articles = []
        now = timezone.now()

        for number in range(7):
            article = Article.objects.create(
                title=f"Django分页文章{number}",
                slug=f"django-page-{number}",
                summary=f"Python分页测试摘要{number}",
                content=f"分页测试正文{number}",
                category=cls.category,
                status=Article.Status.PUBLISHED,
                published_at=now - timedelta(minutes=number),
            )
            article.tags.add(cls.tag)
            cls.articles.append(article)

    def article_list(self, parameters=None):
        return self.client.get(reverse("blog:article_list"), parameters or {})

    def test_first_page_contains_five_articles(self):
        response = self.article_list()

        self.assertEqual(len(response.context["page_obj"].object_list), 5)
        self.assertContains(response, self.articles[0].title)
        self.assertNotContains(response, self.articles[5].title)

    def test_second_page_contains_remaining_articles(self):
        response = self.article_list({"page": 2})

        self.assertEqual(len(response.context["page_obj"].object_list), 2)
        self.assertContains(response, self.articles[5].title)
        self.assertContains(response, self.articles[6].title)

    def test_invalid_page_values_do_not_return_server_error(self):
        for page in ("invalid", "-1", "999"):
            with self.subTest(page=page):
                response = self.article_list({"page": page})
                self.assertEqual(response.status_code, 200)

    def assert_pagination_parameters(self, request_parameters, expected):
        response = self.article_list(request_parameters)

        self.assertTrue(response.context["page_obj"].has_next())
        parsed_parameters = parse_qs(response.context["pagination_query"])
        self.assertEqual(parsed_parameters, expected)

    def test_search_parameter_is_preserved_for_pagination(self):
        self.assert_pagination_parameters(
            {"q": "Django"},
            {"q": ["Django"]},
        )

    def test_category_parameter_is_preserved_for_pagination(self):
        self.assert_pagination_parameters(
            {"category": self.category.slug},
            {"category": [self.category.slug]},
        )

    def test_tag_parameter_is_preserved_for_pagination(self):
        self.assert_pagination_parameters(
            {"tag": self.tag.slug},
            {"tag": [self.tag.slug]},
        )

    def test_combined_parameters_are_preserved_for_pagination(self):
        self.assert_pagination_parameters(
            {
                "q": "Django",
                "category": self.category.slug,
                "tag": self.tag.slug,
            },
            {
                "q": ["Django"],
                "category": [self.category.slug],
                "tag": [self.tag.slug],
            },
        )

    def test_second_page_respects_combined_search_and_filters(self):
        response = self.article_list(
            {
                "q": "Django",
                "category": self.category.slug,
                "tag": self.tag.slug,
                "page": 2,
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"].object_list), 2)
        self.assertTrue(
            all(
                article.category == self.category
                and self.tag in article.tags.all()
                for article in response.context["page_obj"].object_list
            )
        )
