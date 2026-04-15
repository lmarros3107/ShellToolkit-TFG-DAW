from django.db import models


class ShellTemplate(models.Model):
    SHELL_TYPES = [
        ("reverse", "Reverse Shell"),
        ("bind", "Bind Shell"),
    ]
    LANGUAGES = [
        ("bash", "Bash"),
        ("python", "Python"),
        ("php", "PHP"),
        ("powershell", "PowerShell"),
        ("netcat", "Netcat"),
    ]
    OS_CHOICES = [
        ("linux", "Linux"),
        ("windows", "Windows"),
        ("any", "Any"),
    ]

    name = models.CharField(max_length=100)
    shell_type = models.CharField(max_length=20, choices=SHELL_TYPES)
    language = models.CharField(max_length=20, choices=LANGUAGES)
    os = models.CharField(max_length=20, choices=OS_CHOICES, default="any")
    description = models.TextField(blank=True)
    template = models.TextField()
    tags = models.CharField(max_length=200, blank=True)
    difficulty = models.CharField(max_length=20, default="beginner")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["shell_type", "language", "name"]

    def __str__(self):
        return f"{self.name} ({self.shell_type}/{self.language})"
