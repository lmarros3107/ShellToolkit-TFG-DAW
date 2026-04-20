import json

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from listeners.models import ListenerTemplate
from playbooks.models import PlaybookEntry
from recon.models import NmapProfile
from shells.models import ShellTemplate

from .models import SessionFavorite, SessionHistory


def jwt_tool(request):
    # SECURITY: no command execution
    return render(request, "knowledge/jwt.html")


@require_POST
def jwt_log_action(request):
    # SECURITY: no command execution
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid JSON payload."}, status=400)

    action = str(payload.get("action") or "").strip().lower()
    allowed_actions = {"decode", "encode", "verify"}
    if action not in allowed_actions:
        return JsonResponse({"ok": False, "error": "Invalid JWT action."}, status=400)

    # Store only review metadata; do not persist sensitive token/key material.
    raw_input = payload.get("input_data") if isinstance(payload.get("input_data"), dict) else {}
    input_data = {
        "action": action,
        "alg": str(raw_input.get("alg") or "-")[:32],
        "token_parts": int(raw_input.get("token_parts") or 0),
        "warnings": int(raw_input.get("warnings") or 0),
        "finding_counts": raw_input.get("finding_counts") if isinstance(raw_input.get("finding_counts"), dict) else {},
        "signature_status": str(raw_input.get("signature_status") or "unknown")[:32],
    }

    generated_output = str(payload.get("generated_output") or "").strip()[:2000]
    if not generated_output:
        generated_output = "JWT review action executed in browser."

    session_key = _ensure_session_key(request)
    last_row = (
        SessionHistory.objects.filter(session_key=session_key, module="jwt")
        .order_by("-created_at")
        .first()
    )
    if last_row and last_row.input_data == input_data and last_row.generated_output == generated_output:
        return JsonResponse({"ok": True, "history_id": last_row.id, "deduplicated": True})

    row = SessionHistory.objects.create(
        session_key=session_key,
        module="jwt",
        input_data=input_data,
        generated_output=generated_output,
    )

    return JsonResponse({"ok": True, "history_id": row.id, "deduplicated": False})


def history(request):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)
    entries = SessionHistory.objects.filter(session_key=session_key).order_by("-created_at")
    paginator = Paginator(entries, 6)
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages or 1)

    for row in page_obj:
        row.formatted_input_lines = _format_history_input(row.input_data)
        row.favorite_target = _resolve_history_favorite_target(row)
        row.is_already_favorite = False
        if row.favorite_target:
            content_type = ContentType.objects.get(
                app_label=row.favorite_target["app_label"],
                model=row.favorite_target["model"],
            )
            row.is_already_favorite = SessionFavorite.objects.filter(
                session_key=session_key,
                content_type=content_type,
                object_id=row.favorite_target["object_id"],
            ).exists()
        elif row.module in {"encoder", "jwt"}:
            session_history_type = ContentType.objects.get(app_label="knowledge", model="sessionhistory")
            row.is_already_favorite = SessionFavorite.objects.filter(
                session_key=session_key,
                content_type=session_history_type,
                object_id=row.id,
            ).exists()
    return render(
        request,
        "history/history.html",
        {
            "page_obj": page_obj,
            "paginator": paginator,
        },
    )


@require_POST
def clear_history_confirm(request):
    return render(
        request,
        "history/confirm_clear.html",
        {
            "confirm_action": "knowledge:clear_history",
            "cancel_url": "knowledge:history",
            "confirm_title": "Clear history",
            "confirm_message": "Are you sure you want to delete all history entries? This action cannot be undone.",
            "confirm_button": "Yes, delete all",
        },
    )


def clear_history(request):
    # SECURITY: no command execution
    if request.method != "POST":
        return redirect("knowledge:history")

    session_key = _ensure_session_key(request)
    deleted_count, _ = SessionHistory.objects.filter(session_key=session_key).delete()

    if deleted_count:
        messages.success(request, "History cleared successfully.")
    else:
        messages.info(request, "No history entries to clear.")

    return redirect("knowledge:history")


def favorites(request):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)
    favs = SessionFavorite.objects.filter(session_key=session_key).select_related("content_type")

    entries = []
    for favorite in favs:
        obj = favorite.content_object
        if obj is None:
            if favorite.snapshot_url:
                entries.append(
                    {
                        "module": favorite.snapshot_module or favorite.content_type.app_label,
                        "title": favorite.snapshot_title or "Session entry",
                        "summary": favorite.snapshot_summary or "Saved from history.",
                        "url": favorite.snapshot_url,
                        "created_at": favorite.created_at,
                    }
                )
            continue

        url = _build_favorite_url(obj)
        if not url:
            continue

        entries.append(
            {
                "module": _favorite_module_name(obj, favorite.content_type.app_label),
                "title": _favorite_title(obj),
                "summary": _favorite_summary(obj),
                "url": url,
                "created_at": favorite.created_at,
            }
        )

    return render(request, "favorites/favorites.html", {"entries": entries})


@require_POST
def clear_favorites_confirm(request):
    return render(
        request,
        "favorites/confirm_clear.html",
        {
            "confirm_action": "knowledge:clear_favorites",
            "cancel_url": "knowledge:favorites",
            "confirm_title": "Clear favorites",
            "confirm_message": "Are you sure you want to delete all favorites entries? This action cannot be undone.",
            "confirm_button": "Yes, delete all",
        },
    )


def clear_favorites(request):
    # SECURITY: no command execution
    if request.method != "POST":
        return redirect("knowledge:favorites")

    session_key = _ensure_session_key(request)
    deleted_count, _ = SessionFavorite.objects.filter(session_key=session_key).delete()

    if deleted_count:
        messages.success(request, "Favorites cleared successfully.")
    else:
        messages.info(request, "No favorites entries to clear.")

    return redirect("knowledge:favorites")


@require_POST
def add_favorite_from_history(request):
    # SECURITY: no command execution
    session_key = _ensure_session_key(request)
    history_id = (request.POST.get("history_id") or "").strip()
    next_url = (request.POST.get("next") or "").strip() or "knowledge:history"

    if not history_id.isdigit():
        messages.error(request, "Invalid history entry.")
        return redirect(next_url)

    row = SessionHistory.objects.filter(id=int(history_id), session_key=session_key).first()
    if not row:
        messages.error(request, "History entry not found.")
        return redirect(next_url)

    target = _resolve_history_favorite_target(row)
    if not target:
        messages.info(request, "This history entry cannot be saved to favorites.")
        return redirect(next_url)

    content_type = ContentType.objects.get(app_label=target["app_label"], model=target["model"])
    favorite, created = SessionFavorite.objects.get_or_create(
        session_key=session_key,
        content_type=content_type,
        object_id=target["object_id"],
    )

    if created:
        messages.success(request, "Added to favorites.")
    else:
        messages.info(request, "Already saved in favorites.")

    return redirect(next_url)


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
        if app_label == "knowledge" and model == "sessionhistory":
            row = SessionHistory.objects.filter(id=object_id, session_key=session_key).first()
            if row:
                snapshot = _build_session_history_snapshot(row)
                favorite.snapshot_module = snapshot["module"]
                favorite.snapshot_title = snapshot["title"]
                favorite.snapshot_summary = snapshot["summary"]
                favorite.snapshot_url = snapshot["url"]
                favorite.save(
                    update_fields=[
                        "snapshot_module",
                        "snapshot_title",
                        "snapshot_summary",
                        "snapshot_url",
                    ]
                )
        messages.success(request, "Added to favorites.")
    else:
        favorite.delete()
        messages.info(request, "Removed from favorites.")

    return redirect(next_url)


def _ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _build_favorite_url(obj):
    if isinstance(obj, ShellTemplate):
        return reverse("shells:generator")
    if isinstance(obj, ListenerTemplate):
        return reverse("listeners:generator")
    if isinstance(obj, NmapProfile):
        return reverse("recon:nmap_builder")
    if isinstance(obj, PlaybookEntry):
        return reverse("playbooks:detail", kwargs={"slug": obj.slug})
    if isinstance(obj, SessionHistory):
        if obj.module == "encoder":
            return reverse("encoder:tool")
        if obj.module == "jwt":
            return reverse("knowledge:jwt")
    return None


def _favorite_module_name(obj, fallback):
    if isinstance(obj, SessionHistory):
        return obj.module
    return fallback


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
    if isinstance(obj, SessionHistory):
        return obj.generated_output[:220]
    return ""


def _format_history_input(input_data):
    if not isinstance(input_data, dict):
        return []

    label_map = {
        "shell_type": "Shell type",
        "language": "Language",
        "ip": "IP",
        "port": "Port",
        "lhost": "LHOST",
        "lport": "LPORT",
        "encoding": "Encoding",
        "scan_type": "Scan type",
        "action": "Action",
        "alg": "Algorithm",
        "token_parts": "Token parts",
        "warnings": "Warnings",
        "signature_status": "Signature status",
    }
    shell_type_map = {
        "reverse": "Reverse Shell",
        "bind": "Bind Shell",
    }
    language_map = {
        "bash": "Bash",
        "python": "Python",
        "php": "PHP",
        "powershell": "PowerShell",
        "netcat": "Netcat",
    }

    lines = []
    for key, value in input_data.items():
        key_text = str(key)
        if key_text in {"template_id", "id", "session_key"} or key_text.endswith("_id"):
            continue

        label = label_map.get(key_text, key_text.replace("_", " ").capitalize())
        display_value = _format_history_value(value)

        if key_text == "shell_type":
            display_value = shell_type_map.get(str(value).strip().lower(), display_value)
        elif key_text == "language":
            display_value = language_map.get(str(value).strip().lower(), display_value)

        lines.append({"label": label, "value": display_value})

    return lines


def _format_history_value(value):
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in value.items())
    text = str(value).strip()
    return text or "-"


def _resolve_history_favorite_target(row):
    if not isinstance(row.input_data, dict):
        return None

    template_id = row.input_data.get("template_id")
    if not isinstance(template_id, int):
        return None

    if row.module == "shells":
        if ShellTemplate.objects.filter(id=template_id, is_active=True).exists():
            return {"app_label": "shells", "model": "shelltemplate", "object_id": template_id}
        return None

    if row.module == "listeners":
        if ListenerTemplate.objects.filter(id=template_id, is_active=True).exists():
            return {"app_label": "listeners", "model": "listenertemplate", "object_id": template_id}
        return None

    return None


def _build_session_history_snapshot(row):
    action = ""
    if isinstance(row.input_data, dict):
        action = str(row.input_data.get("action") or "").strip().lower()

    if row.module == "jwt":
        title = f"JWT {action or 'review'}"
        return {
            "module": "jwt",
            "title": title,
            "summary": row.generated_output[:220] or "JWT entry saved from history.",
            "url": reverse("knowledge:jwt"),
        }

    if row.module == "encoder":
        title = "Encoder output"
        return {
            "module": "encoder",
            "title": title,
            "summary": row.generated_output[:220] or "Encoder entry saved from history.",
            "url": reverse("encoder:tool"),
        }

    return {
        "module": row.module,
        "title": "Session entry",
        "summary": row.generated_output[:220] or "Saved from history.",
        "url": reverse("knowledge:history"),
    }


