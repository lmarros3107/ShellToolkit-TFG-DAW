from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    # SECURITY: no command execution
    return render(request, "core/home.html")


def health_check(request):
    # SECURITY: no command execution
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        db_ok = False

    payload = {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
    }
    return JsonResponse(payload, status=200 if db_ok else 503)


def error_403(request, exception=None):
    return render(request, "403.html", status=403)


def error_404(request, exception=None):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)
