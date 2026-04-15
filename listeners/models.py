from django.db import models


class ListenerTemplate(models.Model):
    TOOLS = [
        ("netcat", "Netcat"),
        ("socat", "Socat"),
        ("metasploit", "Metasploit Handler"),
    ]

    name = models.CharField(max_length=100)
    tool = models.CharField(max_length=20, choices=TOOLS)
    description = models.TextField(blank=True)
    template = models.TextField()
    tags = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["tool", "name"]

    def __str__(self):
        return f"{self.name} ({self.tool})"
