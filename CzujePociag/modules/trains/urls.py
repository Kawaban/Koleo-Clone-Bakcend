from django.urls import path

from modules.trains import views

urlpatterns = [
    path("trains/<str:train_number>/", views.TrainsView.as_view()),
]