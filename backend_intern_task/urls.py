from django.urls import path

from . import views

app_name = "backend_intern_task"
urlpatterns = [
  path("init", views.GoogleCalendarInitView.as_view(), name="google-calendar-init"),
]
