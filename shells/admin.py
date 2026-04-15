from django.contrib import admin

from .models import ShellTemplate


@admin.register(ShellTemplate)
class ShellTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "shell_type", "language", "os", "difficulty", "is_active")
    search_fields = ("name", "language", "tags", "description")
    list_filter = ("shell_type", "language", "os", "difficulty", "is_active")
