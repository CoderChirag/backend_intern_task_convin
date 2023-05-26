from django.urls import path

from . import views

app_name = "backend_intern_task"
urlpatterns = [
    path("", views.index, name="index"),
]
