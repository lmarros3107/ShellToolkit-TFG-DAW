from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import migrations


def load_seed_data(apps, schema_editor):
    data_path = Path(settings.BASE_DIR) / "data.json"
    if not data_path.exists():
        return

    call_command("loaddata", str(data_path), verbosity=1)


class Migration(migrations.Migration):

    dependencies = [
        ("knowledge", "0004_sessionfavorite_snapshot_fields"),
        ("listeners", "0001_initial"),
        ("playbooks", "0003_add_windows_playbooks"),
        ("recon", "0001_initial"),
        ("shells", "0002_add_netcat_reverse"),
    ]

    operations = [
        migrations.RunPython(load_seed_data, migrations.RunPython.noop),
    ]
