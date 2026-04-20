from django.urls import path

from favorites import views as favorites_views
from . import views

app_name = "knowledge"

urlpatterns = [
    path("jwt/", views.jwt_tool, name="jwt"),
    path("jwt/log/", views.jwt_log_action, name="jwt_log_action"),
    path("history/", views.history, name="history"),
    path("history/add-favorite/", views.add_favorite_from_history, name="add_favorite_from_history"),
    path("history/clear/confirm/", views.clear_history_confirm, name="clear_history_confirm"),
    path("history/clear/", views.clear_history, name="clear_history"),
    path("favorites/", views.favorites, name="favorites"),
    path("favorites/<int:favorite_id>/", views.favorite_detail, name="favorite_detail"),
    path("favorites/<int:favorite_id>/delete/confirm/", favorites_views.delete_favorite_confirm, name="delete_favorite_confirm"),
    path("favorites/<int:favorite_id>/delete/", favorites_views.delete_favorite, name="delete_favorite"),
    path("favorites/clear/confirm/", views.clear_favorites_confirm, name="clear_favorites_confirm"),
    path("favorites/clear/", views.clear_favorites, name="clear_favorites"),
    path("favorites/toggle/", views.toggle_favorite, name="toggle_favorite"),
]
