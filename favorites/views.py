from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from knowledge.models import SessionFavorite


@require_POST
def delete_favorite_confirm(request, favorite_id):
    if not request.session.session_key:
        request.session.create()

    favorite_exists = SessionFavorite.objects.filter(
        id=favorite_id,
        session_key=request.session.session_key,
    ).exists()
    if not favorite_exists:
        messages.info(request, "Favorite entry not found.")
        return redirect("knowledge:favorites")

    return render(
        request,
        "favorites/confirm_delete.html",
        {
            "confirm_title": "Remove favorite",
            "confirm_message": "Are you sure you want to remove this favorite entry?",
            "confirm_button": "Yes, remove",
            "action_url": reverse("knowledge:delete_favorite", kwargs={"favorite_id": favorite_id}),
            "cancel_url": reverse("knowledge:favorite_detail", kwargs={"favorite_id": favorite_id}),
            "next_url": reverse("knowledge:favorites"),
        },
    )


@require_POST
def delete_favorite(request, favorite_id):
    if not request.session.session_key:
        request.session.create()

    deleted_count, _ = SessionFavorite.objects.filter(
        id=favorite_id,
        session_key=request.session.session_key,
    ).delete()

    if deleted_count:
        messages.success(request, "Favorite removed successfully.")
    else:
        messages.info(request, "Favorite entry not found.")

    next_url = (request.POST.get("next") or "").strip() or reverse("knowledge:favorites")
    return redirect(next_url)

