from django.contrib import admin

from .models import ListenerTemplate


@admin.register(ListenerTemplate)
class ListenerTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "tool", "is_active")
    search_fields = ("name", "tool", "tags", "description")
    list_filter = ("tool", "is_active")
