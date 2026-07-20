from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from blog.forms import CommentForm
from blog.models import Article, Comment


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="author")
        self.article = Article.objects.create(
            title="评论模型测试文章",
            slug="comment-model-article",
            summary="摘要",
            content="正文",
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content="一条测试评论",
        )

    def test_string_representation_is_clear(self):
        self.assertEqual(
            str(self.comment),
            f"{self.user} 对《{self.article}》的评论",
        )

    def test_comment_references_article(self):
        self.assertEqual(self.comment.article, self.article)
        self.assertIn(self.comment, self.article.comments.all())

    def test_comment_references_user(self):
        self.assertEqual(self.comment.author, self.user)
        self.assertIn(self.comment, self.user.article_comments.all())

    def test_deleting_article_deletes_comment(self):
        comment_pk = self.comment.pk

        self.article.delete()

        self.assertFalse(Comment.objects.filter(pk=comment_pk).exists())

    def test_deleting_user_deletes_comment(self):
        comment_pk = self.comment.pk

        self.user.delete()

        self.assertFalse(Comment.objects.filter(pk=comment_pk).exists())

    def test_content_max_length_is_500(self):
        self.assertEqual(Comment._meta.get_field("content").max_length, 500)

    def test_form_rejects_empty_content(self):
        self.assertFalse(CommentForm({"content": ""}).is_valid())

    def test_form_rejects_whitespace_only_content(self):
        form = CommentForm({"content": "   \n "})

        self.assertFalse(form.is_valid())
        self.assertIn("评论内容不能为空", form.errors["content"])

    def test_form_rejects_content_longer_than_500_characters(self):
        self.assertFalse(CommentForm({"content": "a" * 501}).is_valid())

    def test_comment_is_registered_in_admin(self):
        self.assertIn(Comment, admin.site._registry)
