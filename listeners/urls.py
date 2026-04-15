from django.urls import path

from . import views

app_name = "listeners"

urlpatterns = [
    path("", views.generator, name="generator"),
]

