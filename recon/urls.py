from django.urls import path

from . import views

app_name = "recon"

urlpatterns = [
    path("", views.nmap_builder, name="nmap_builder"),
]

