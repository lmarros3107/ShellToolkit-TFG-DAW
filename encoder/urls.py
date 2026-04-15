from django.urls import path

from . import views

app_name = "encoder"

urlpatterns = [
    path("", views.tool, name="tool"),
]

