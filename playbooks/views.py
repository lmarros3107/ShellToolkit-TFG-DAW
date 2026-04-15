from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render

from knowledge.models import SessionFavorite

from .models import PlaybookEntry


def linux_list(request):
    # SECURITY: no command execution
    entries = PlaybookEntry.objects.filter(platform="linux", is_active=True)
    categories = sorted({entry.category for entry in entries})

    context = {
        "entries": entries,
        "categories": categories,
        "platform_label": "Linux",
    }
    return render(request, "playbooks/linux_list.html", context)


def windows_list(request):
    # SECURITY: no command execution
    entries = PlaybookEntry.objects.filter(platform="windows", is_active=True)
    categories = sorted({entry.category for entry in entries})

    context = {
        "entries": entries,
        "categories": categories,
        "platform_label": "Windows",
    }
    return render(request, "playbooks/windows_list.html", context)


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
