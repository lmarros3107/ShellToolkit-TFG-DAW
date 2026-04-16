import re

from django import forms


class NmapBuilderForm(forms.Form):
    TARGET_IPV4_REGEX = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
    TARGET_IPV4_CIDR_REGEX = re.compile(r"^(\d{1,3}\.){3}\d{1,3}/([0-9]|[12][0-9]|3[0-2])$")
    TARGET_RANGE_REGEX = re.compile(r"^(\d{1,3}\.){3}\d{1,3}-\d{1,3}$")
    TARGET_DOMAIN_REGEX = re.compile(r"^(?=.{1,253}$)([a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}$")
    CUSTOM_PORTS_REGEX = re.compile(r"^[0-9,\-\s]+$")
    EXTRA_FLAGS_FORBIDDEN_REGEX = re.compile(r"[;&|`$<>\\\n\r]")

    NSE_CHOICES = [
        ("auth", "auth"),
        ("brute", "brute"),
        ("default", "default"),
        ("discovery", "discovery"),
        ("safe", "safe"),
        ("version", "version"),
        ("vuln", "vuln"),
    ]

    SCAN_TYPE_CHOICES = [
        ("basic", "Basic discovery (-sV -sC)"),
        ("stealth", "Stealth SYN (-sS)"),
        ("udp", "UDP focus (-sU)"),
        ("vuln", "Vuln scripts (--script vuln)"),
        ("full", "Full TCP (-p-)"),
    ]

    PORT_MODE_CHOICES = [
        ("top100", "Top 100 ports"),
        ("top1000", "Top 1000 ports"),
        ("all", "All ports"),
        ("custom", "Custom ports"),
    ]

    TIMING_CHOICES = [(str(i), f"T{i}") for i in range(0, 6)]

    target = forms.CharField(max_length=253, required=True, strip=True)
    scan_type = forms.ChoiceField(choices=SCAN_TYPE_CHOICES, required=True)
    port_mode = forms.ChoiceField(choices=PORT_MODE_CHOICES, required=True)
    custom_ports = forms.CharField(max_length=120, required=False, strip=True)
    timing = forms.ChoiceField(choices=TIMING_CHOICES, required=True)
    nse_categories = forms.MultipleChoiceField(
        choices=NSE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    extra_flags = forms.CharField(max_length=200, required=False, strip=True)

    def clean_target(self):
        value = (self.cleaned_data.get("target") or "").strip()
        if not value:
            raise forms.ValidationError("Target is required.")

        if self.TARGET_IPV4_REGEX.match(value):
            self._validate_ipv4(value)
            return value

        if self.TARGET_IPV4_CIDR_REGEX.match(value):
            self._validate_ipv4(value.split("/")[0])
            return value

        if self.TARGET_RANGE_REGEX.match(value):
            self._validate_ipv4_range(value)
            return value

        if self.TARGET_DOMAIN_REGEX.match(value):
            return value.lower()

        raise forms.ValidationError("Enter a valid IPv4, CIDR, domain, or simple IPv4 range.")

    def clean_custom_ports(self):
        value = (self.cleaned_data.get("custom_ports") or "").strip()
        if not value:
            return ""

        if not self.CUSTOM_PORTS_REGEX.match(value):
            raise forms.ValidationError("Custom ports can include only numbers, commas, and hyphens.")

        for chunk in [item.strip() for item in value.split(",") if item.strip()]:
            self._validate_port_chunk(chunk)

        return value

    def clean_extra_flags(self):
        value = (self.cleaned_data.get("extra_flags") or "").strip()
        if not value:
            return ""

        if self.EXTRA_FLAGS_FORBIDDEN_REGEX.search(value):
            raise forms.ValidationError("Extra flags contain forbidden shell metacharacters.")

        return value

    def clean(self):
        cleaned_data = super().clean()
        port_mode = cleaned_data.get("port_mode")
        custom_ports = cleaned_data.get("custom_ports", "")

        if port_mode == "custom" and not custom_ports:
            self.add_error("custom_ports", "Custom ports are required when port mode is custom.")

        return cleaned_data

    def _validate_ipv4(self, value):
        octets = value.split(".")
        if len(octets) != 4:
            raise forms.ValidationError("Invalid IPv4 format.")
        for octet in octets:
            octet_int = int(octet)
            if octet_int < 0 or octet_int > 255:
                raise forms.ValidationError("IPv4 octets must be between 0 and 255.")

    def _validate_ipv4_range(self, value):
        left, right = value.split("-")
        self._validate_ipv4(left)
        end_value = int(right)
        if end_value < 0 or end_value > 255:
            raise forms.ValidationError("Range end octet must be between 0 and 255.")
        start_last = int(left.split(".")[-1])
        if end_value < start_last:
            raise forms.ValidationError("Range end octet must be greater than or equal to start octet.")

    def _validate_port_chunk(self, chunk):
        if "-" in chunk:
            bounds = chunk.split("-", 1)
            if len(bounds) != 2 or not bounds[0].isdigit() or not bounds[1].isdigit():
                raise forms.ValidationError("Invalid custom port range format.")
            start, end = int(bounds[0]), int(bounds[1])
            if start < 1 or end > 65535 or start > end:
                raise forms.ValidationError("Custom port ranges must be between 1 and 65535.")
            return

        if not chunk.isdigit():
            raise forms.ValidationError("Custom ports must be numeric.")

        port = int(chunk)
        if port < 1 or port > 65535:
            raise forms.ValidationError("Custom ports must be between 1 and 65535.")
