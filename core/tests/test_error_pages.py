from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.views.defaults import server_error


class ErrorPageTests(TestCase):
    @override_settings(DEBUG=False)
    def test_unknown_url_uses_custom_404_page(self):
        response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "没有找到这个页面", status_code=404)
        self.assertContains(response, reverse("core:home"), status_code=404)

    @override_settings(DEBUG=False)
    def test_default_server_error_uses_safe_custom_500_page(self):
        request = RequestFactory().get("/temporary-error/")

        with self.assertTemplateUsed("500.html"):
            response = server_error(request)

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "服务器暂时出现问题", status_code=500)
        self.assertNotContains(response, "Traceback", status_code=500)
