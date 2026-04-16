from django.urls import path

from . import views

app_name = "playbooks"

urlpatterns = [
    path("", views.playbook_list, name="list"),
    path("linux/", views.linux_list, name="linux_list"),
    path("windows/", views.windows_list, name="windows_list"),
    path("<slug:slug>/", views.detail, name="detail"),
]
