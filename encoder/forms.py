from django import forms


class EncoderForm(forms.Form):
    ENCODING_CHOICES = [
        ("base64", "Base64"),
        ("url", "URL Encode"),
        ("hex", "Hex Encode"),
    ]

    input_text = forms.CharField(
        max_length=2000,
        required=False,
        strip=True,
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Enter text to encode"}),
    )
    encoding_type = forms.ChoiceField(choices=ENCODING_CHOICES, required=True)

    def clean_input_text(self):
        value = (self.cleaned_data.get("input_text") or "").strip()
        if not value:
            raise forms.ValidationError("Input text is required.")
        return value
