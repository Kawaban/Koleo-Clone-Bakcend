from django.urls import path

from modules.users import views

urlpatterns = [
    path("tickets/", views.TicketView.as_view()),
]