from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from social.models import SocialPost


class SocialFeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username="feed-user")
        cls.other_user = User.objects.create_user(username="other-feed-user")
        cls.staff = User.objects.create_user(
            username="feed-staff",
            is_staff=True,
        )
        cls.personal_post = SocialPost.objects.create(
            feed_type=SocialPost.FeedType.PERSONAL,
            author=cls.staff,
            content="个人主页专属动态",
        )
        cls.circle_post = SocialPost.objects.create(
            feed_type=SocialPost.FeedType.CIRCLE,
            author=cls.user,
            content="圈专属动态",
        )

    def test_guest_can_browse_personal_and_circle_feeds(self):
        self.assertEqual(
            self.client.get(reverse("social:personal_feed")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("social:circle_feed")).status_code,
            200,
        )

    def test_personal_feed_only_displays_personal_posts(self):
        response = self.client.get(reverse("social:personal_feed"))

        self.assertContains(response, self.personal_post.content)
        self.assertNotContains(response, self.circle_post.content)

    def test_circle_feed_displays_circle_and_personal_posts(self):
        response = self.client.get(reverse("social:circle_feed"))

        self.assertContains(response, self.circle_post.content)
        self.assertContains(response, self.personal_post.content)

    def test_personal_post_is_visible_to_guests_in_circle_feed(self):
        response = self.client.get(reverse("social:circle_feed"))

        self.assertContains(response, self.personal_post.content)

    def test_guest_sees_login_prompt_without_publish_form(self):
        response = self.client.get(reverse("social:circle_feed"))

        self.assertContains(response, "登录")
        self.assertNotContains(response, "发布到圈")

    def test_logged_in_user_can_create_circle_post(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("social:circle_feed"),
            {"content": "用户新动态"},
        )

        created = SocialPost.objects.get(content="用户新动态")
        self.assertEqual(created.author, self.user)
        self.assertEqual(created.feed_type, SocialPost.FeedType.CIRCLE)
        self.assertRedirects(response, reverse("social:circle_feed"))

    def test_guest_cannot_create_circle_post(self):
        response = self.client.post(
            reverse("social:circle_feed"),
            {"content": "游客伪造动态"},
        )

        self.assertFalse(
            SocialPost.objects.filter(content="游客伪造动态").exists()
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_author_and_feed_type_from_post_data_are_ignored(self):
        self.client.force_login(self.user)

        self.client.post(
            reverse("social:circle_feed"),
            {
                "content": "伪造字段动态",
                "author": self.other_user.pk,
                "feed_type": SocialPost.FeedType.PERSONAL,
            },
        )

        created = SocialPost.objects.get(content="伪造字段动态")
        self.assertEqual(created.author, self.user)
        self.assertEqual(created.feed_type, SocialPost.FeedType.CIRCLE)

    def test_get_request_does_not_create_post(self):
        self.client.force_login(self.user)
        before_count = SocialPost.objects.count()

        response = self.client.get(
            reverse("social:circle_feed"),
            {"content": "GET伪造动态"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SocialPost.objects.count(), before_count)

    def test_invalid_post_returns_bad_request_without_saving(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("social:circle_feed"),
            {"content": "   "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            SocialPost.objects.filter(author=self.user, content="").exists()
        )

    def test_feed_paginates_ten_posts_per_page_newest_first(self):
        SocialPost.objects.filter(feed_type=SocialPost.FeedType.CIRCLE).delete()
        posts = []
        for number in range(12):
            post = SocialPost.objects.create(
                feed_type=SocialPost.FeedType.CIRCLE,
                author=self.user,
                content=f"分页动态{number}",
            )
            SocialPost.objects.filter(pk=post.pk).update(
                created_at=timezone.now() + timedelta(minutes=number)
            )
            posts.append(post)

        response = self.client.get(reverse("social:circle_feed"))

        self.assertEqual(len(response.context["posts"]), 10)
        self.assertEqual(
            response.context["posts"][0].pk,
            posts[-1].pk,
        )
        self.assertContains(response, posts[-1].content)
        self.assertNotContains(response, posts[0].content)

    def test_empty_feeds_show_friendly_messages(self):
        SocialPost.objects.all().delete()

        personal = self.client.get(reverse("social:personal_feed"))
        circle = self.client.get(reverse("social:circle_feed"))

        self.assertContains(personal, "暂时还没有个人主页动态")
        self.assertContains(circle, "圈里暂时还没有动态")
