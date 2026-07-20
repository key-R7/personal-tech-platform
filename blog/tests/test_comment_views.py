from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Article, Comment


class CommentViewTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create_user(username="comment-author")
        cls.other_user = User.objects.create_user(username="other-user")
        cls.staff_user = User.objects.create_user(
            username="staff-user",
            is_staff=True,
        )
        cls.public_article = Article.objects.create(
            title="公开评论文章",
            slug="public-comment-article",
            summary="摘要",
            content="正文",
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.other_article = Article.objects.create(
            title="另一篇公开文章",
            slug="other-comment-article",
            summary="摘要",
            content="正文",
            status=Article.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        cls.draft_article = Article.objects.create(
            title="评论草稿文章",
            slug="draft-comment-article",
            summary="摘要",
            content="正文",
            status=Article.Status.DRAFT,
        )
        cls.without_date_article = Article.objects.create(
            title="评论无发布时间文章",
            slug="without-date-comment-article",
            summary="摘要",
            content="正文",
            status=Article.Status.PUBLISHED,
        )

    def create_url(self, article=None):
        article = article or self.public_article
        return reverse("blog:comment_create", kwargs={"slug": article.slug})

    def delete_url(self, comment):
        return reverse("blog:comment_delete", kwargs={"pk": comment.pk})


class CommentCreateTests(CommentViewTestData):
    def test_logged_in_user_can_comment_on_public_article(self):
        self.client.force_login(self.author)

        response = self.client.post(self.create_url(), {"content": "公开评论"})

        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().content, "公开评论")
        self.assertRedirects(response, self.public_article.get_absolute_url())

    def test_saved_author_is_current_user(self):
        self.client.force_login(self.author)

        self.client.post(self.create_url(), {"content": "作者测试"})

        self.assertEqual(Comment.objects.get().author, self.author)

    def test_saved_article_comes_from_url(self):
        self.client.force_login(self.author)

        self.client.post(self.create_url(), {"content": "文章测试"})

        self.assertEqual(Comment.objects.get().article, self.public_article)

    def test_guest_cannot_create_comment(self):
        response = self.client.post(self.create_url(), {"content": "游客评论"})

        self.assertEqual(Comment.objects.count(), 0)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_empty_comment_is_rejected(self):
        self.client.force_login(self.author)

        response = self.client.post(self.create_url(), {"content": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)

    def test_whitespace_only_comment_is_rejected(self):
        self.client.force_login(self.author)

        response = self.client.post(self.create_url(), {"content": "   \n "})

        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "评论内容不能为空",
            status_code=400,
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_longer_than_500_characters_is_rejected(self):
        self.client.force_login(self.author)

        response = self.client.post(self.create_url(), {"content": "a" * 501})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Comment.objects.count(), 0)

    def test_get_request_cannot_create_comment(self):
        self.client.force_login(self.author)

        response = self.client.get(self.create_url())

        self.assertEqual(response.status_code, 405)
        self.assertEqual(Comment.objects.count(), 0)

    def test_draft_article_cannot_receive_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            self.create_url(self.draft_article),
            {"content": "草稿评论"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 0)

    def test_article_without_published_at_cannot_receive_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            self.create_url(self.without_date_article),
            {"content": "未发布评论"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 0)

    def test_unknown_article_slug_cannot_receive_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("blog:comment_create", kwargs={"slug": "not-found"}),
            {"content": "无效文章评论"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 0)

    def test_forged_author_and_article_values_are_ignored(self):
        self.client.force_login(self.author)

        self.client.post(
            self.create_url(),
            {
                "content": "伪造字段测试",
                "author": self.other_user.pk,
                "article": self.other_article.pk,
            },
        )

        comment = Comment.objects.get()
        self.assertEqual(comment.author, self.author)
        self.assertEqual(comment.article, self.public_article)

    def test_comment_creation_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.author)

        response = csrf_client.post(self.create_url(), {"content": "无CSRF评论"})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 0)


class CommentDisplayTests(CommentViewTestData):
    def test_detail_only_displays_comments_for_current_article(self):
        own_comment = Comment.objects.create(
            article=self.public_article,
            author=self.author,
            content="当前文章评论",
        )
        other_comment = Comment.objects.create(
            article=self.other_article,
            author=self.other_user,
            content="其他文章评论",
        )

        response = self.client.get(self.public_article.get_absolute_url())

        self.assertContains(response, own_comment.content)
        self.assertNotContains(response, other_comment.content)

    def test_guest_can_see_public_comment(self):
        comment = Comment.objects.create(
            article=self.public_article,
            author=self.author,
            content="游客可见评论",
        )

        response = self.client.get(self.public_article.get_absolute_url())

        self.assertContains(response, comment.content)
        self.assertContains(response, self.author.username)

    def test_comment_content_is_escaped(self):
        Comment.objects.create(
            article=self.public_article,
            author=self.author,
            content="<script>alert('xss')</script>",
        )

        response = self.client.get(self.public_article.get_absolute_url())

        self.assertContains(response, "&lt;script&gt;", html=False)
        self.assertNotContains(response, "<script>alert('xss')</script>", html=False)

    def test_empty_comments_show_friendly_message(self):
        response = self.client.get(self.public_article.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "暂时还没有评论")

    def test_logged_in_user_sees_comment_form_and_csrf_token(self):
        self.client.force_login(self.author)

        response = self.client.get(self.public_article.get_absolute_url())

        self.assertContains(response, self.create_url())
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "提交评论")

    def test_guest_sees_login_prompt_instead_of_comment_form(self):
        response = self.client.get(self.public_article.get_absolute_url())

        self.assertContains(response, "登录")
        self.assertNotContains(response, "提交评论")


class CommentDeleteTests(CommentViewTestData):
    def setUp(self):
        self.comment = Comment.objects.create(
            article=self.public_article,
            author=self.author,
            content="等待删除的评论",
        )

    def test_author_can_delete_own_comment(self):
        self.client.force_login(self.author)

        response = self.client.post(self.delete_url(self.comment))

        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertRedirects(response, self.public_article.get_absolute_url())

    def test_other_user_cannot_delete_comment(self):
        self.client.force_login(self.other_user)

        with self.assertLogs("blog.views", level="WARNING") as captured_logs:
            response = self.client.post(self.delete_url(self.comment))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertIn("attempted to delete comment", captured_logs.output[0])

    def test_staff_user_can_delete_any_comment(self):
        self.client.force_login(self.staff_user)

        response = self.client.post(self.delete_url(self.comment))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_guest_cannot_delete_comment(self):
        response = self.client.post(self.delete_url(self.comment))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_get_request_cannot_delete_comment(self):
        self.client.force_login(self.author)

        response = self.client.get(self.delete_url(self.comment))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_unknown_comment_returns_not_found(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("blog:comment_delete", kwargs={"pk": 999999})
        )

        self.assertEqual(response.status_code, 404)

    def test_changing_comment_id_does_not_bypass_permission(self):
        own_comment = Comment.objects.create(
            article=self.public_article,
            author=self.other_user,
            content="其他用户自己的评论",
        )
        self.client.force_login(self.other_user)

        response = self.client.post(self.delete_url(self.comment))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())
        self.assertTrue(Comment.objects.filter(pk=own_comment.pk).exists())

    def test_delete_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.author)

        response = csrf_client.post(self.delete_url(self.comment))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())
