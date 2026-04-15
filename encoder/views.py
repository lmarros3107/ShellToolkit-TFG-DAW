import base64
from urllib.parse import quote

from django.contrib import messages
from django.shortcuts import render

from knowledge.models import SessionHistory

from .forms import EncoderForm


def tool(request):
    # SECURITY: no command execution
    encoded_output = ""
    selected_encoding = ""
    form = EncoderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        input_text = form.cleaned_data["input_text"]
        selected_encoding = form.cleaned_data["encoding_type"]

        if selected_encoding == "base64":
            encoded_output = base64.b64encode(input_text.encode("utf-8")).decode("utf-8")
        elif selected_encoding == "url":
            encoded_output = quote(input_text, safe="")
        elif selected_encoding == "hex":
            encoded_output = input_text.encode("utf-8").hex()

        if not request.session.session_key:
            request.session.create()

        SessionHistory.objects.create(
            session_key=request.session.session_key,
            module="encoder",
            input_data={
                "encoding_type": selected_encoding,
                "input_text": input_text,
            },
            generated_output=encoded_output,
        )
        messages.success(request, "Text encoded successfully.")

    context = {
        "form": form,
        "encoded_output": encoded_output,
        "selected_encoding": selected_encoding,
    }
    return render(request, "encoder/tool.html", context)
