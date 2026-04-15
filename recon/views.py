from django.contrib import messages
from django.shortcuts import render

from knowledge.models import SessionHistory

from .forms import NmapBuilderForm
from .utils import build_nmap_command


def nmap_builder(request):
    # SECURITY: no command execution
    build_result = None
    form = NmapBuilderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        build_result = build_nmap_command(form.cleaned_data)

        if not request.session.session_key:
            request.session.create()

        SessionHistory.objects.create(
            session_key=request.session.session_key,
            module="recon",
            input_data={
                "target": form.cleaned_data["target"],
                "scan_type": form.cleaned_data["scan_type"],
                "port_mode": form.cleaned_data["port_mode"],
                "custom_ports": form.cleaned_data.get("custom_ports", ""),
                "timing": form.cleaned_data["timing"],
                "nse_categories": form.cleaned_data.get("nse_categories", []),
                "extra_flags": form.cleaned_data.get("extra_flags", ""),
            },
            generated_output=build_result["command"],
        )
        messages.success(request, "Nmap command generated successfully.")

    context = {
        "form": form,
        "build_result": build_result,
    }
    return render(request, "recon/nmap_builder.html", context)
