from django.test import TestCase
from django.urls import reverse

from django.contrib.contenttypes.models import ContentType

from .models import SessionFavorite, SessionHistory


class JwtViewsTests(TestCase):
    def test_jwt_page_loads(self):
        response = self.client.get(reverse("knowledge:jwt"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "JWT")
        self.assertContains(response, "Decode")
        self.assertNotContains(response, "Notes &amp; Findings")

    def test_legacy_knowledge_route_removed(self):
        response = self.client.get("/knowledge/")
        self.assertEqual(response.status_code, 404)

    def test_jwt_log_action_creates_history_row(self):
        response = self.client.post(
            reverse("knowledge:jwt_log_action"),
            data={
                "action": "decode",
                "input_data": {
                    "alg": "HS256",
                    "token_parts": 3,
                    "warnings": 1,
                    "signature_status": "not-run",
                    "finding_counts": {"info": 1},
                },
                "generated_output": "JWT decode review",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SessionHistory.objects.count(), 1)
        self.assertEqual(SessionHistory.objects.first().module, "jwt")

    def test_jwt_log_action_deduplicates_consecutive_equal_entries(self):
        payload = {
            "action": "decode",
            "input_data": {
                "alg": "HS256",
                "token_parts": 3,
                "warnings": 0,
                "signature_status": "not-run",
            },
            "generated_output": "JWT decode review",
        }

        first = self.client.post(
            reverse("knowledge:jwt_log_action"),
            data=payload,
            content_type="application/json",
        )
        second = self.client.post(
            reverse("knowledge:jwt_log_action"),
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(SessionHistory.objects.count(), 1)
        self.assertTrue(second.json().get("deduplicated"))

    def test_toggle_favorite_with_jwt_history_uses_existing_flow(self):
        session = self.client.session
        session.save()
        row = SessionHistory.objects.create(
            session_key=session.session_key,
            module="jwt",
            input_data={"action": "verify", "alg": "HS256"},
            generated_output="JWT verify review",
        )

        response = self.client.post(
            reverse("knowledge:toggle_favorite"),
            {
                "app_label": "knowledge",
                "model": "sessionhistory",
                "object_id": str(row.id),
                "next": reverse("knowledge:history"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("knowledge:history"))
        self.assertEqual(SessionFavorite.objects.count(), 1)

        favorites_response = self.client.get(reverse("knowledge:favorites"))
        self.assertEqual(favorites_response.status_code, 200)
        self.assertContains(favorites_response, "jwt")
        self.assertContains(favorites_response, "/jwt/")

    def test_history_view_lists_jwt_rows(self):
        session = self.client.session
        session.save()
        SessionHistory.objects.create(
            session_key=session.session_key,
            module="jwt",
            input_data={"action": "decode", "alg": "none"},
            generated_output="JWT decode review",
        )

        response = self.client.get(reverse("knowledge:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "jwt")
        self.assertContains(response, "JWT decode review")
        self.assertContains(response, "Add to favorites")

    def test_toggle_favorite_removes_existing_item(self):
        session = self.client.session
        session.save()
        history_row = SessionHistory.objects.create(
            session_key=session.session_key,
            module="jwt",
            input_data={"action": "decode"},
            generated_output="JWT decode review",
        )
        content_type = ContentType.objects.get(app_label="knowledge", model="sessionhistory")
        SessionFavorite.objects.create(
            session_key=session.session_key,
            content_type=content_type,
            object_id=history_row.id,
        )

        response = self.client.post(
            reverse("knowledge:toggle_favorite"),
            {
                "app_label": "knowledge",
                "model": "sessionhistory",
                "object_id": str(history_row.id),
                "next": reverse("knowledge:favorites"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SessionFavorite.objects.count(), 0)

    def test_jwt_favorite_persists_after_history_clear(self):
        session = self.client.session
        session.save()
        row = SessionHistory.objects.create(
            session_key=session.session_key,
            module="jwt",
            input_data={"action": "verify", "alg": "HS256"},
            generated_output="JWT verify review",
        )

        self.client.post(
            reverse("knowledge:toggle_favorite"),
            {
                "app_label": "knowledge",
                "model": "sessionhistory",
                "object_id": str(row.id),
                "next": reverse("knowledge:history"),
            },
        )
        self.assertEqual(SessionFavorite.objects.count(), 1)

        self.client.post(reverse("knowledge:clear_history"))
        self.assertEqual(SessionHistory.objects.count(), 0)
        self.assertEqual(SessionFavorite.objects.count(), 1)

        favorites_response = self.client.get(reverse("knowledge:favorites"))
        self.assertEqual(favorites_response.status_code, 200)
        self.assertContains(favorites_response, "JWT verify")
        self.assertContains(favorites_response, "/jwt/")

