from django.urls import path

from . import views

app_name = "knowledge"

urlpatterns = [
    path("knowledge/", views.index, name="index"),
    path("knowledge/<slug:slug>/", views.detail, name="detail"),
    path("history/", views.history, name="history"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/toggle/", views.toggle_favorite, name="toggle_favorite"),
]
