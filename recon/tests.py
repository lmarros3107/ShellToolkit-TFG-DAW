from django.test import TestCase
from django.urls import reverse

from knowledge.models import SessionHistory

from .forms import NmapBuilderForm
from .utils import build_nmap_command


class NmapBuilderFormTests(TestCase):
    def test_rejects_metacharacters_in_extra_flags(self):
        form = NmapBuilderForm(
            data={
                "target": "scanme.nmap.org",
                "scan_type": "basic",
                "port_mode": "top100",
                "custom_ports": "",
                "timing": "3",
                "nse_categories": ["default"],
                "extra_flags": "-Pn; whoami",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("extra_flags", form.errors)

    def test_requires_custom_ports_when_mode_is_custom(self):
        form = NmapBuilderForm(
            data={
                "target": "192.168.1.10",
                "scan_type": "basic",
                "port_mode": "custom",
                "custom_ports": "",
                "timing": "2",
                "nse_categories": ["safe"],
                "extra_flags": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("custom_ports", form.errors)


class NmapBuilderUtilsTests(TestCase):
    def test_build_command_returns_expected_structure(self):
        result = build_nmap_command(
            {
                "target": "10.10.10.10",
                "scan_type": "basic",
                "port_mode": "top100",
                "custom_ports": "",
                "timing": "3",
                "nse_categories": ["default", "safe"],
                "extra_flags": "-Pn",
            }
        )

        self.assertIn("command", result)
        self.assertIn("explanations", result)
        self.assertIn("noise_level", result)
        self.assertIn("nmap", result["command"])


class NmapBuilderViewTests(TestCase):
    def test_build_view_generates_command_and_saves_history(self):
        response = self.client.post(
            reverse("recon:nmap_builder"),
            {
                "target": "scanme.nmap.org",
                "scan_type": "basic",
                "port_mode": "top1000",
                "custom_ports": "",
                "timing": "3",
                "nse_categories": ["default"],
                "extra_flags": "-Pn",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nmap")
        self.assertEqual(SessionHistory.objects.filter(module="recon").count(), 1)

    def test_builds_basic_command(self):
        response = self.client.post(
            reverse("recon:nmap_builder"),
            {
                "target": "127.0.0.1",
                "scan_type": "basic",
                "port_mode": "top100",
                "timing": "2",
                "nse_categories": ["default"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nmap")
        self.assertEqual(SessionHistory.objects.filter(module="recon").count(), 1)

    def test_handles_optional_fields(self):
        response = self.client.post(
            reverse("recon:nmap_builder"),
            {
                "target": "127.0.0.1",
                "scan_type": "basic",
                "port_mode": "custom",
                "custom_ports": "22,80",
                "timing": "2",
                "nse_categories": ["safe"],
                "extra_flags": "--open",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nmap")
        self.assertEqual(SessionHistory.objects.filter(module="recon").count(), 1)

    def test_builds_full_command(self):
        response = self.client.post(
            reverse("recon:nmap_builder"),
            {
                "target": "127.0.0.1",
                "scan_type": "full",
                "port_mode": "all",
                "timing": "4",
                "nse_categories": ["default"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nmap")
        self.assertEqual(SessionHistory.objects.filter(module="recon").count(), 1)

    def test_accepts_vuln_scan(self):
        response = self.client.post(
            reverse("recon:nmap_builder"),
            {
                "target": "127.0.0.1",
                "scan_type": "vuln",
                "port_mode": "top1000",
                "timing": "3",
                "nse_categories": ["safe"],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nmap")
        self.assertEqual(SessionHistory.objects.filter(module="recon").count(), 1)
