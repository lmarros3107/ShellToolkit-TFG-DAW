from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

from knowledge.models import SessionFavorite, SessionHistory

from .forms import ShellGenerateForm
from .models import ShellTemplate


def generator(request):
    # SECURITY: no command execution
    generated_command = ""
    selected_template = None
    is_favorite = False
    form = ShellGenerateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        shell_type = form.cleaned_data["shell_type"]
        language = form.cleaned_data["language"]
        ip_value = form.cleaned_data.get("ip", "")
        port_value = str(form.cleaned_data["port"])

        selected_template = (
            ShellTemplate.objects.filter(
                shell_type=shell_type,
                language=language,
                is_active=True,
            )
            .order_by("id")
            .first()
        )

        if not selected_template:
            messages.error(request, "No active template found for the selected shell type and language.")
        else:
            generated_command = selected_template.template.replace("{ip}", ip_value).replace("{port}", port_value)

            if not request.session.session_key:
                request.session.create()

            SessionHistory.objects.create(
                session_key=request.session.session_key,
                module="shells",
                input_data={
                    "shell_type": shell_type,
                    "language": language,
                    "ip": ip_value,
                    "port": port_value,
                    "template_id": selected_template.id,
                },
                generated_output=generated_command,
            )
            messages.success(request, "Command generated successfully.")

    if selected_template:
        if not request.session.session_key:
            request.session.create()
        content_type = ContentType.objects.get(app_label="shells", model="shelltemplate")
        is_favorite = SessionFavorite.objects.filter(
            session_key=request.session.session_key,
            content_type=content_type,
            object_id=selected_template.id,
        ).exists()

    context = {
        "form": form,
        "generated_command": generated_command,
        "selected_template": selected_template,
        "is_favorite": is_favorite,
    }
    return render(request, "shells/generator.html", context)
