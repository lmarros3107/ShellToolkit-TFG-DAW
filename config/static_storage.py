from django.contrib.staticfiles.storage import StaticFilesStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage


def _prefix_relative_static_url(base_url, built_url):
    if not base_url:
        return built_url

    # If the URL is already absolute/root-relative, keep it untouched.
    if built_url.startswith(("/", "http://", "https://", "data:")):
        return built_url

    return f"{base_url.rstrip('/')}/{built_url.lstrip('/')}"


class SafeStaticFilesStorage(StaticFilesStorage):
    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")

        built_url = super().url(name)
        return _prefix_relative_static_url(self.base_url, built_url)


class SafeCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    def url(self, name, force=False):
        built_url = super().url(name, force=force)
        return _prefix_relative_static_url(self.base_url, built_url)


