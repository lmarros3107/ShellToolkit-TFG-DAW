"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("core.urls")),
    path("", include("knowledge.urls")),
    path("shells/", include("shells.urls")),
    path("listeners/", include("listeners.urls")),
    path("encoder/", include("encoder.urls")),
    path("recon/", include("recon.urls")),
    path("playbooks/", include("playbooks.urls")),
]

if settings.DEBUG:
    # Keep /static/ resolution ahead of app URL includes during local development.
    urlpatterns = staticfiles_urlpatterns() + urlpatterns

handler403 = core_views.error_403
handler404 = core_views.error_404
handler500 = core_views.error_500
