from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from listeners.models import ListenerTemplate
from playbooks.models import PlaybookEntry
from recon.models import NmapProfile
from shells.models import ShellTemplate

from .models import SessionFavorite, SessionHistory


def index(request):
    # SECURITY: no command execution
    query = (request.GET.get("q") or "").strip()
    module_filter = (request.GET.get("module") or "").strip().lower()
    platform_filter = (request.GET.get("platform") or "").strip().lower()
    technique_filter = (request.GET.get("technique") or "").strip().lower()
    difficulty_filter = (request.GET.get("difficulty") or "").strip().lower()

    entries = []
    entries.extend(_shell_entries(query))
    entries.extend(_listener_entries(query))
    entries.extend(_recon_entries(query))
    entries.extend(_playbook_entries(query))

    filtered_entries = _apply_filters(
        entries=entries,
        module_filter=module_filter,
        platform_filter=platform_filter,
        technique_filter=technique_filter,
        difficulty_filter=difficulty_filter,
    )

    all_entries = _shell_entries("") + _listener_entries("") + _recon_entries("") + _playbook_entries("")
    technique_options = sorted({item["technique"] for item in all_entries if item["technique"]})
    difficulty_options = sorted({item["difficulty"] for item in all_entries if item["difficulty"] and item["difficulty"] != "n/a"})

    context = {
        "entries": sorted(filtered_entries, key=lambda item: (item["module"], item["title"].lower())),
        "query": query,
        "active_module": module_filter,
        "active_platform": platform_filter,
        "active_technique": technique_filter,
        "active_difficulty": difficulty_filter,
        "module_options": ["shells", "listeners", "recon", "playbooks"],
        "platform_options": ["linux", "windows", "any"],
        "technique_options": technique_options,
        "difficulty_options": difficulty_options,
    }
    return render(request, "knowledge/index.html", context)


def detail(request, slug):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)

    if slug.startswith("shells-"):
        object_id = _parse_int_suffix(slug, "shells-")
        shell = get_object_or_404(ShellTemplate, id=object_id, is_active=True)
        detail_data = {
            "module": "shells",
            "title": shell.name,
            "summary": shell.description or shell.template,
            "platform": shell.os,
            "technique": f"{shell.shell_type}/{shell.language}",
            "difficulty": shell.difficulty,
            "tags": shell.tags,
            "body": shell.template,
            "app_label": "shells",
            "model": "shelltemplate",
            "object_id": shell.id,
        }
    elif slug.startswith("listeners-"):
        object_id = _parse_int_suffix(slug, "listeners-")
        listener = get_object_or_404(ListenerTemplate, id=object_id, is_active=True)
        detail_data = {
            "module": "listeners",
            "title": listener.name,
            "summary": listener.description or listener.template,
            "platform": "any",
            "technique": listener.tool,
            "difficulty": "n/a",
            "tags": listener.tags,
            "body": listener.template,
            "app_label": "listeners",
            "model": "listenertemplate",
            "object_id": listener.id,
        }
    elif slug.startswith("recon-"):
        object_id = _parse_int_suffix(slug, "recon-")
        recon = get_object_or_404(NmapProfile, id=object_id, is_active=True)
        detail_data = {
            "module": "recon",
            "title": recon.name,
            "summary": recon.description,
            "platform": "any",
            "technique": recon.scan_type,
            "difficulty": recon.noise_level,
            "tags": recon.nse_categories,
            "body": recon.extra_flags or recon.lab_notes,
            "app_label": "recon",
            "model": "nmapprofile",
            "object_id": recon.id,
        }
    elif slug.startswith("playbooks-"):
        playbook_slug = slug[len("playbooks-") :]
        playbook = get_object_or_404(PlaybookEntry, slug=playbook_slug, is_active=True)
        detail_data = {
            "module": "playbooks",
            "title": playbook.title,
            "summary": playbook.summary,
            "platform": playbook.platform,
            "technique": playbook.category,
            "difficulty": playbook.difficulty,
            "tags": playbook.tags,
            "body": playbook.commands,
            "app_label": "playbooks",
            "model": "playbookentry",
            "object_id": playbook.id,
        }
    else:
        raise Http404("Knowledge entry not found")

    content_type = ContentType.objects.get(app_label=detail_data["app_label"], model=detail_data["model"])
    detail_data["is_favorite"] = SessionFavorite.objects.filter(
        session_key=session_key,
        content_type=content_type,
        object_id=detail_data["object_id"],
    ).exists()

    return render(request, "knowledge/detail.html", {"entry": detail_data})


def history(request):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)
    rows = SessionHistory.objects.filter(session_key=session_key).order_by("-created_at")
    return render(request, "knowledge/history.html", {"rows": rows})


def favorites(request):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)
    favs = SessionFavorite.objects.filter(session_key=session_key).select_related("content_type")

    entries = []
    for favorite in favs:
        obj = favorite.content_object
        if obj is None:
            continue

        knowledge_slug = _build_knowledge_slug(obj)
        if not knowledge_slug:
            continue

        entries.append(
            {
                "module": favorite.content_type.app_label,
                "title": _favorite_title(obj),
                "summary": _favorite_summary(obj),
                "slug": knowledge_slug,
                "created_at": favorite.created_at,
            }
        )

    return render(request, "knowledge/favorites.html", {"entries": entries})


@require_POST
def toggle_favorite(request):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)

    app_label = (request.POST.get("app_label") or "").strip().lower()
    model = (request.POST.get("model") or "").strip().lower()
    object_id_value = (request.POST.get("object_id") or "").strip()
    next_url = (request.POST.get("next") or "/favorites/").strip()

    if not app_label or not model or not object_id_value.isdigit():
        messages.error(request, "Invalid favorite toggle request.")
        return redirect(next_url)

    content_type = get_object_or_404(ContentType, app_label=app_label, model=model)
    object_id = int(object_id_value)

    favorite, created = SessionFavorite.objects.get_or_create(
        session_key=session_key,
        content_type=content_type,
        object_id=object_id,
    )

    if created:
        messages.success(request, "Added to favorites.")
    else:
        favorite.delete()
        messages.info(request, "Removed from favorites.")

    return redirect(next_url)


def _shell_entries(query):
    queryset = ShellTemplate.objects.filter(is_active=True)
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(template__icontains=query)
            | Q(tags__icontains=query)
            | Q(language__icontains=query)
            | Q(shell_type__icontains=query)
        )

    return [
        {
            "module": "shells",
            "title": obj.name,
            "summary": obj.description or obj.template[:220],
            "platform": obj.os,
            "technique": f"{obj.shell_type}/{obj.language}",
            "difficulty": obj.difficulty,
            "slug": f"shells-{obj.id}",
        }
        for obj in queryset
    ]


def _listener_entries(query):
    queryset = ListenerTemplate.objects.filter(is_active=True)
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(template__icontains=query)
            | Q(tags__icontains=query)
            | Q(tool__icontains=query)
        )

    return [
        {
            "module": "listeners",
            "title": obj.name,
            "summary": obj.description or obj.template[:220],
            "platform": "any",
            "technique": obj.tool,
            "difficulty": "n/a",
            "slug": f"listeners-{obj.id}",
        }
        for obj in queryset
    ]


def _recon_entries(query):
    queryset = NmapProfile.objects.filter(is_active=True)
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(scan_type__icontains=query)
            | Q(nse_categories__icontains=query)
            | Q(extra_flags__icontains=query)
            | Q(lab_notes__icontains=query)
        )

    return [
        {
            "module": "recon",
            "title": obj.name,
            "summary": obj.description or obj.lab_notes or obj.extra_flags,
            "platform": "any",
            "technique": obj.scan_type,
            "difficulty": obj.noise_level,
            "slug": f"recon-{obj.id}",
        }
        for obj in queryset
    ]


def _playbook_entries(query):
    queryset = PlaybookEntry.objects.filter(is_active=True)
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(category__icontains=query)
            | Q(tags__icontains=query)
            | Q(summary__icontains=query)
            | Q(commands__icontains=query)
            | Q(explanation__icontains=query)
        )

    return [
        {
            "module": "playbooks",
            "title": obj.title,
            "summary": obj.summary,
            "platform": obj.platform,
            "technique": obj.category,
            "difficulty": obj.difficulty,
            "slug": f"playbooks-{obj.slug}",
        }
        for obj in queryset
    ]


def _apply_filters(entries, module_filter, platform_filter, technique_filter, difficulty_filter):
    filtered = entries

    if module_filter:
        filtered = [entry for entry in filtered if entry["module"] == module_filter]

    if platform_filter:
        filtered = [entry for entry in filtered if entry["platform"] == platform_filter]

    if technique_filter:
        filtered = [entry for entry in filtered if technique_filter in entry["technique"].lower()]

    if difficulty_filter:
        filtered = [entry for entry in filtered if difficulty_filter in entry["difficulty"].lower()]

    return filtered


def _parse_int_suffix(slug, prefix):
    value = slug[len(prefix) :]
    if not value.isdigit():
        raise Http404("Invalid knowledge entry")
    return int(value)


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _build_knowledge_slug(obj):
    if isinstance(obj, ShellTemplate):
        return f"shells-{obj.id}"
    if isinstance(obj, ListenerTemplate):
        return f"listeners-{obj.id}"
    if isinstance(obj, NmapProfile):
        return f"recon-{obj.id}"
    if isinstance(obj, PlaybookEntry):
        return f"playbooks-{obj.slug}"
    return ""


def _favorite_title(obj):
    if hasattr(obj, "name"):
        return obj.name
    if hasattr(obj, "title"):
        return obj.title
    return str(obj)


def _favorite_summary(obj):
    if isinstance(obj, ShellTemplate):
        return obj.description or obj.template[:200]
    if isinstance(obj, ListenerTemplate):
        return obj.description or obj.template[:200]
    if isinstance(obj, NmapProfile):
        return obj.description or obj.lab_notes or obj.extra_flags
    if isinstance(obj, PlaybookEntry):
        return obj.summary
    return ""

