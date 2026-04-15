from django.test import TestCase
from django.urls import reverse

from .models import PlaybookEntry


class PlaybookViewsTests(TestCase):
    def setUp(self):
        self.linux_entry = PlaybookEntry.objects.create(
            title="Linux Enumeration Quickstart",
            slug="linux-enumeration-quickstart",
            platform="linux",
            category="enumeration",
            tags="enum,linux",
            summary="Baseline host enumeration commands.",
            prerequisites="Shell access",
            commands="id\nuname -a\nwhoami",
            explanation="Collect identity and kernel context first.",
            warnings="Run only in authorized lab machines.",
            difficulty="beginner",
            is_active=True,
        )
        self.windows_entry = PlaybookEntry.objects.create(
            title="Windows Service Enumeration",
            slug="windows-service-enumeration",
            platform="windows",
            category="services",
            tags="windows,services",
            summary="Enumerate service metadata and start permissions.",
            prerequisites="cmd or powershell shell",
            commands="sc query state= all\nwmic service get name,displayname,startmode,state",
            explanation="Focuses on weak service configurations.",
            warnings="Run only on authorized lab hosts.",
            difficulty="beginner",
            is_active=True,
        )

    def test_linux_list_view(self):
        response = self.client.get(reverse("playbooks:linux_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.linux_entry.title)
        self.assertNotContains(response, self.windows_entry.title)

    def test_windows_list_view(self):
        response = self.client.get(reverse("playbooks:windows_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.windows_entry.title)
        self.assertNotContains(response, self.linux_entry.title)

    def test_detail_view(self):
        response = self.client.get(reverse("playbooks:detail", kwargs={"slug": self.linux_entry.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "id")
