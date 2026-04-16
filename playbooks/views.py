from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render

from knowledge.models import SessionFavorite

from .models import PlaybookEntry


def playbook_list(request):
    # SECURITY: no command execution
    context = _build_list_context(request)
    return render(request, "playbooks/list.html", context)


def linux_list(request):
    # SECURITY: no command execution
    context = _build_list_context(request, default_platform="linux")
    return render(request, "playbooks/list.html", context)


def windows_list(request):
    # SECURITY: no command execution
    context = _build_list_context(request, default_platform="windows")
    return render(request, "playbooks/list.html", context)


def detail(request, slug):
    # SECURITY: no command execution
    entry = get_object_or_404(PlaybookEntry, slug=slug, is_active=True)

    if not request.session.session_key:
        request.session.create()

    content_type = ContentType.objects.get(app_label="playbooks", model="playbookentry")
    is_favorite = SessionFavorite.objects.filter(
        session_key=request.session.session_key,
        content_type=content_type,
        object_id=entry.id,
    ).exists()

    context = {
        "entry": entry,
        "is_favorite": is_favorite,
    }
    return render(request, "playbooks/detail.html", context)


def _build_list_context(request, default_platform=""):
    platform = (request.GET.get("platform") or "").strip().lower()
    valid_platforms = {"linux", "windows"}
    if platform in valid_platforms:
        current_platform = platform
    elif default_platform in valid_platforms:
        current_platform = default_platform
    else:
        current_platform = ""

    entries = PlaybookEntry.objects.filter(is_active=True)
    if current_platform:
        entries = entries.filter(platform=current_platform)

    categories = sorted({entry.category for entry in entries})

    return {
        "entries": entries,
        "categories": categories,
        "current_platform": current_platform,
    }

