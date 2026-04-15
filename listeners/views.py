from django.contrib import messages
from django.shortcuts import render

from knowledge.models import SessionHistory

from .forms import ListenerGenerateForm
from .models import ListenerTemplate


def generator(request):
    # SECURITY: no command execution
    generated_command = ""
    selected_template = None
    form = ListenerGenerateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        tool = form.cleaned_data["tool"]
        ip_value = form.cleaned_data.get("ip", "")
        port_value = str(form.cleaned_data["port"])

        selected_template = (
            ListenerTemplate.objects.filter(tool=tool, is_active=True)
            .order_by("id")
            .first()
        )

        if not selected_template:
            messages.error(request, "No active listener template found for the selected tool.")
        else:
            generated_command = selected_template.template.replace("{ip}", ip_value).replace("{port}", port_value)

            if not request.session.session_key:
                request.session.create()

            SessionHistory.objects.create(
                session_key=request.session.session_key,
                module="listeners",
                input_data={
                    "tool": tool,
                    "ip": ip_value,
                    "port": port_value,
                    "template_id": selected_template.id,
                },
                generated_output=generated_command,
            )
            messages.success(request, "Listener command generated successfully.")

    context = {
        "form": form,
        "generated_command": generated_command,
        "selected_template": selected_template,
    }
    return render(request, "listeners/generator.html", context)
