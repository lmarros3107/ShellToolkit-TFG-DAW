from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from knowledge.models import SessionFavorite


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

    return redirect('/favorites/')

