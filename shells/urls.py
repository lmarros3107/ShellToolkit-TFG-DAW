from django.urls import path

from . import views

app_name = "shells"

urlpatterns = [
    path("", views.generator, name="generator"),
]

