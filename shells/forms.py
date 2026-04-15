import re

from django import forms

from .models import ShellTemplate


class ShellGenerateForm(forms.Form):
    IPV4_REGEX = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")

    ip = forms.CharField(max_length=15, required=False)
    port = forms.IntegerField(min_value=1, max_value=65535, required=True)
    shell_type = forms.ChoiceField(choices=ShellTemplate.SHELL_TYPES, required=True)
    language = forms.ChoiceField(choices=ShellTemplate.LANGUAGES, required=True)

    def clean_ip(self):
        value = (self.cleaned_data.get("ip") or "").strip()
        if not value:
            return ""

        if not self.IPV4_REGEX.match(value):
            raise forms.ValidationError("Invalid IPv4 format.")

        octets = value.split(".")
        if any(int(octet) < 0 or int(octet) > 255 for octet in octets):
            raise forms.ValidationError("IPv4 octets must be between 0 and 255.")

        return value

    def clean(self):
        cleaned_data = super().clean()
        shell_type = cleaned_data.get("shell_type")
        ip_value = cleaned_data.get("ip", "")

        if shell_type == "reverse" and not ip_value:
            self.add_error("ip", "IP is required for reverse shells.")

        return cleaned_data

