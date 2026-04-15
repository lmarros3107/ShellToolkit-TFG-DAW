from django.db import models


class NmapProfile(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    scan_type = models.CharField(max_length=50)
    nse_categories = models.CharField(max_length=200, blank=True)
    extra_flags = models.CharField(max_length=300, blank=True)
    noise_level = models.CharField(max_length=20, default="low")
    lab_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
