from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    SENSITIVE_PREFIXES = (
        "/shells/",
        "/listeners/",
        "/encoder/",
        "/recon/",
        "/knowledge/",
        "/history/",
        "/favorites/",
    )

    def process_response(self, request, response):
        csp_value = getattr(settings, "CSP_HEADER", "")
        report_uri = getattr(settings, "CSP_REPORT_URI", "")

        if csp_value:
            if report_uri:
                csp_value = f"{csp_value} report-uri {report_uri};"
            response["Content-Security-Policy"] = csp_value

        response["Permissions-Policy"] = getattr(
            settings,
            "PERMISSIONS_POLICY",
            "geolocation=(), microphone=(), camera=(), payment=(), usb=()",
        )
        response["Referrer-Policy"] = getattr(
            settings,
            "SECURE_REFERRER_POLICY",
            "strict-origin-when-cross-origin",
        )
        response["X-Content-Type-Options"] = "nosniff"
        response["X-XSS-Protection"] = "1; mode=block"

        if any(request.path.startswith(prefix) for prefix in self.SENSITIVE_PREFIXES):
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        return response


class RateLimitMiddleware:
    POST_LIMIT = 30
    GLOBAL_LIMIT = 200
    WINDOW = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_exempt(request.path):
            return self.get_response(request)

        ip_address = self._get_client_ip(request)

        if not self._increment_and_check(f"rl:global:{ip_address}", self.GLOBAL_LIMIT):
            return self._too_many_requests(request)

        if request.method == "POST":
            if not self._increment_and_check(f"rl:post:{ip_address}", self.POST_LIMIT):
                return self._too_many_requests(request)

        return self.get_response(request)

    @staticmethod
    def _is_exempt(path):
        admin_prefix = "/" + settings.ADMIN_URL.strip("/") + "/"
        return path.startswith("/static/") or path.startswith("/admin/") or path.startswith(admin_prefix)

    @staticmethod
    def _get_client_ip(request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    def _increment_and_check(self, key, limit):
        added = cache.add(key, 1, timeout=self.WINDOW)
        if added:
            return True

        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=self.WINDOW)
            return True

        return count <= limit

    @staticmethod
    def _too_many_requests(request):
        return render(request, "429.html", status=429)

