from django.contrib import admin

from .models import NmapProfile


@admin.register(NmapProfile)
class NmapProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "scan_type", "noise_level", "is_active")
    search_fields = ("name", "description", "nse_categories", "extra_flags", "lab_notes")
    list_filter = ("scan_type", "noise_level", "is_active")
