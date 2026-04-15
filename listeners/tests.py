from django.test import TestCase
from django.urls import reverse

from knowledge.models import SessionHistory

from .models import ListenerTemplate


class ListenerGeneratorViewTests(TestCase):
    def setUp(self):
        ListenerTemplate.objects.create(
            name="Test Netcat Listener",
            tool="netcat",
            template="nc -lvnp {port}",
            is_active=True,
        )
        ListenerTemplate.objects.create(
            name="Test Metasploit Handler",
            tool="metasploit",
            template="set LHOST {ip}; set LPORT {port}",
            is_active=True,
        )

    def test_generate_listener_and_store_history(self):
        response = self.client.post(
            reverse("listeners:generator"),
            {
                "tool": "netcat",
                "ip": "",
                "port": 5555,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nc -lvnp 5555")
        self.assertEqual(SessionHistory.objects.filter(module="listeners").count(), 1)

    def test_metasploit_requires_ip(self):
        response = self.client.post(
            reverse("listeners:generator"),
            {
                "tool": "metasploit",
                "ip": "",
                "port": 4444,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "IP is required for metasploit handlers.")

