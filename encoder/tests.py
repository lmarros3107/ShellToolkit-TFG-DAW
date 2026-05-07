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
                "action": "encode",
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
                "action": "encode",
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
                "action": "encode",
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
                "action": "encode",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Input text is required.")

    def test_base64_decoding_and_history(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "aGVsbG8gd29ybGQ=",
                "encoding_type": "base64",
                "action": "decode",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "hello world")
        history = SessionHistory.objects.filter(module="encoder").first()
        self.assertIsNotNone(history)
        self.assertEqual(history.input_data.get("action"), "decode")

    def test_url_decoding(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "a%20b%2Fc",
                "encoding_type": "url",
                "action": "decode",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "a b/c")

    def test_hex_decoding(self):
        response = self.client.post(
            reverse("encoder:tool"),
            {
                "input_text": "414243",
                "encoding_type": "hex",
                "action": "decode",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ABC")
