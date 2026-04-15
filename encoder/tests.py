import base64
from urllib.parse import quote

from django.test import TestCase
from django.urls import reverse

from knowledge.models import SessionHistory


class EncoderToolViewTests(TestCase):
    def test_base64_encoding_and_history(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "hello world",
                "encoding_type": "base64",
            },
        )

        expected = base64.b64encode("hello world".encode("utf-8")).decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected)
        self.assertEqual(SessionHistory.objects.filter(module="encoder").count(), 1)

    def test_url_encoding(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "a b/c",
                "encoding_type": "url",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, quote("a b/c", safe=""))

    def test_hex_encoding(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "ABC",
                "encoding_type": "hex",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "414243")

    def test_input_is_required(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "   ",
                "encoding_type": "base64",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Input text is required.")

