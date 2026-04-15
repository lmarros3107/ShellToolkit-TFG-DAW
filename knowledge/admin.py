from django.contrib import admin

from .models import SessionFavorite, SessionHistory


@admin.register(SessionHistory)
class SessionHistoryAdmin(admin.ModelAdmin):
    list_display = ("module", "session_key", "created_at")
    search_fields = ("module", "session_key", "generated_output")
    list_filter = ("module", "created_at")


@admin.register(SessionFavorite)
class SessionFavoriteAdmin(admin.ModelAdmin):
    list_display = ("session_key", "content_type", "object_id", "created_at")
    search_fields = ("session_key", "content_type__model", "object_id")
    list_filter = ("content_type", "created_at")
