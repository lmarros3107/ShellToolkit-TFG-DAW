import base64
import binascii
from urllib.parse import quote, unquote

from django.contrib import messages
from django.shortcuts import render

from knowledge.models import SessionHistory

from .forms import EncoderForm


def tool(request):
    # SECURITY: no command execution
    encoded_output = ""
    selected_encoding = ""
    selected_action = "encode"
    form = EncoderForm(request.POST or None)

    if request.method == "POST":
        selected_action = (form.data.get("action") or "encode").strip().lower()

    if request.method == "POST" and form.is_valid():
        input_text = form.cleaned_data["input_text"]
        selected_encoding = form.cleaned_data["encoding_type"]
        selected_action = form.cleaned_data["action"]
        succeeded = True

        try:
            if selected_action == "encode":
                if selected_encoding == "base64":
                    encoded_output = base64.b64encode(input_text.encode("utf-8")).decode("utf-8")
                elif selected_encoding == "url":
                    encoded_output = quote(input_text, safe="")
                elif selected_encoding == "hex":
                    encoded_output = input_text.encode("utf-8").hex()
            else:
                if selected_encoding == "base64":
                    decoded_bytes = base64.b64decode(input_text, validate=True)
                    encoded_output = decoded_bytes.decode("utf-8")
                elif selected_encoding == "url":
                    encoded_output = unquote(input_text)
                elif selected_encoding == "hex":
                    decoded_bytes = bytes.fromhex(input_text)
                    encoded_output = decoded_bytes.decode("utf-8")
        except (binascii.Error, ValueError, UnicodeDecodeError):
            succeeded = False
            encoded_output = ""
            messages.error(request, "Unable to decode the provided input.")

        if succeeded:
            if not request.session.session_key:
                request.session.create()

            SessionHistory.objects.create(
                session_key=request.session.session_key,
                module="encoder",
                input_data={
                    "action": selected_action,
                    "encoding_type": selected_encoding,
                    "input_text": input_text,
                },
                generated_output=encoded_output,
            )
            if selected_action == "decode":
                messages.success(request, "Text decoded successfully.")
            else:
                messages.success(request, "Text encoded successfully.")

    context = {
        "form": form,
        "encoded_output": encoded_output,
        "selected_encoding": selected_encoding,
        "selected_action": selected_action,
    }
    return render(request, "encoder/tool.html", context)
