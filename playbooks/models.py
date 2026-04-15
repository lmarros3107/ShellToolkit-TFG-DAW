from django.db import models


class PlaybookEntry(models.Model):
    PLATFORMS = [
        ("linux", "Linux"),
        ("windows", "Windows"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=300, blank=True)
    summary = models.TextField()
    prerequisites = models.TextField(blank=True)
    commands = models.TextField()
    explanation = models.TextField(blank=True)
    warnings = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, default="beginner")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["platform", "category", "title"]

    def __str__(self):
        return f"{self.title} ({self.platform})"
