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

    def test_jwt_log_action_rejects_invalid_numeric_fields(self):
        response = self.client.post(
            reverse("knowledge:jwt_log_action"),
            data={
                "action": "decode",
                "input_data": {
                    "alg": "HS256",
                    "token_parts": "invalid",
                    "warnings": 0,
                    "signature_status": "not-run",
                },
                "generated_output": "JWT decode review",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(SessionHistory.objects.count(), 0)

    def test_jwt_log_action_rejects_oversized_payload(self):
        response = self.client.post(
            reverse("knowledge:jwt_log_action"),
            data={
                "action": "decode",
                "input_data": {
                    "alg": "HS256",
                    "token_parts": 3,
                    "warnings": 0,
                    "signature_status": "not-run",
                },
                "generated_output": "A" * 10000,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(SessionHistory.objects.count(), 0)

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
        self.assertContains(
            favorites_response,
            reverse("knowledge:favorite_detail", kwargs={"favorite_id": SessionFavorite.objects.first().id}),
        )

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
        self.assertContains(favorites_response, "Open detail")

    def test_favorite_detail_allows_back_and_individual_delete(self):
        session = self.client.session
        session.save()
        row = SessionHistory.objects.create(
            session_key=session.session_key,
            module="jwt",
            input_data={"action": "decode", "alg": "HS256"},
            generated_output="JWT decode review",
        )
        content_type = ContentType.objects.get(app_label="knowledge", model="sessionhistory")
        favorite = SessionFavorite.objects.create(
            session_key=session.session_key,
            content_type=content_type,
            object_id=row.id,
            snapshot_module="jwt",
            snapshot_title="JWT decode",
            snapshot_summary="JWT decode review",
            snapshot_url=reverse("knowledge:jwt"),
        )

        detail_response = self.client.get(reverse("knowledge:favorite_detail", kwargs={"favorite_id": favorite.id}))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Back to Favorites")
        self.assertContains(detail_response, "Remove favorite")

        confirm_response = self.client.post(
            reverse("knowledge:delete_favorite_confirm", kwargs={"favorite_id": favorite.id}),
        )
        self.assertEqual(confirm_response.status_code, 200)
        self.assertContains(confirm_response, "Confirmation required")
        self.assertContains(confirm_response, reverse("knowledge:favorite_detail", kwargs={"favorite_id": favorite.id}))

        delete_response = self.client.post(
            reverse("knowledge:delete_favorite", kwargs={"favorite_id": favorite.id}),
            {"next": reverse("knowledge:favorites")},
        )
        self.assertEqual(delete_response.status_code, 302)
        self.assertEqual(delete_response.url, reverse("knowledge:favorites"))
        self.assertEqual(SessionFavorite.objects.count(), 0)

