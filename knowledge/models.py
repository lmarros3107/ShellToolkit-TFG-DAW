from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class SessionHistory(models.Model):
    session_key = models.CharField(max_length=40)
    module = models.CharField(max_length=50)
    input_data = models.JSONField(default=dict)
    generated_output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.module} @ {self.created_at:%Y-%m-%d %H:%M:%S}"


class SessionFavorite(models.Model):
    session_key = models.CharField(max_length=40)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("session_key", "content_type", "object_id")

    def __str__(self):
        return f"favorite {self.content_type.model}:{self.object_id}"
