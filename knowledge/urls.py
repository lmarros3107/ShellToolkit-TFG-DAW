from django.urls import path

from . import views

app_name = "knowledge"

urlpatterns = [
    path("knowledge/", views.index, name="index"),
    path("knowledge/<slug:slug>/", views.detail, name="detail"),
    path("history/", views.history, name="history"),
    path("history/add-favorite/", views.add_favorite_from_history, name="add_favorite_from_history"),
    path("history/clear/confirm/", views.clear_history_confirm, name="clear_history_confirm"),
    path("history/clear/", views.clear_history, name="clear_history"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/clear/confirm/", views.clear_favorites_confirm, name="clear_favorites_confirm"),
    path("favorites/clear/", views.clear_favorites, name="clear_favorites"),
    path("favorites/toggle/", views.toggle_favorite, name="toggle_favorite"),
]
