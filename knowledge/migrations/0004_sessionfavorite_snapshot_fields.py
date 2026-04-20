from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("knowledge", "0003_add_nmap_knowledge"),
    ]

    operations = [
        migrations.AddField(
            model_name="sessionfavorite",
            name="snapshot_module",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AddField(
            model_name="sessionfavorite",
            name="snapshot_summary",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="sessionfavorite",
            name="snapshot_title",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="sessionfavorite",
            name="snapshot_url",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]

