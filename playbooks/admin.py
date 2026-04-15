from django.contrib import admin

from .models import PlaybookEntry


@admin.register(PlaybookEntry)
class PlaybookEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "platform", "category", "difficulty", "is_active")
    search_fields = ("title", "category", "tags", "summary", "commands")
    list_filter = ("platform", "category", "difficulty", "is_active")
    prepopulated_fields = {"slug": ("title",)}
