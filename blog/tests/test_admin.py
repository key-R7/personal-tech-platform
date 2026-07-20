from django.contrib import admin
from django.test import TestCase

from blog.admin import ArticleAdmin, CategoryAdmin, TagAdmin
from blog.models import Article, Category, Tag


class BlogAdminTests(TestCase):
    def test_taxonomy_models_are_registered(self):
        self.assertIsInstance(admin.site._registry[Category], CategoryAdmin)
        self.assertIsInstance(admin.site._registry[Tag], TagAdmin)

    def test_article_admin_supports_category_and_tag_filtering(self):
        article_admin = admin.site._registry[Article]

        self.assertIsInstance(article_admin, ArticleAdmin)
        self.assertIn("category", article_admin.list_filter)
        self.assertIn("tags", article_admin.list_filter)
        self.assertIn("tags", article_admin.filter_horizontal)
