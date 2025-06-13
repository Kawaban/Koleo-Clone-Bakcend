from django.urls import path

from modules.connections import views

urlpatterns = [
    path("connections/", views.ConnectionsView.as_view()),
    path("stations/", views.StationView.as_view()),
]