from django.test import TestCase


class HomeStaticUrlsTests(TestCase):
    def test_home_uses_static_prefix_for_assets(self):
        response = self.client.get("/", HTTP_HOST="127.0.0.1")

        self.assertContains(response, 'href="/static/css/theme.css"')
        self.assertContains(response, 'href="/static/css/base.css"')
        self.assertContains(response, 'href="/static/css/components.css"')
        self.assertContains(response, 'src="/static/js/app.js"')
        self.assertContains(response, 'src="/static/js/copy.js"')
        self.assertContains(response, 'src="/static/js/nav.js"')

    def test_home_nav_links_include_jwt_and_remove_knowledge(self):
        response = self.client.get("/", HTTP_HOST="127.0.0.1")

        self.assertContains(response, 'href="/jwt/"')
        self.assertNotContains(response, 'href="/knowledge/"')

