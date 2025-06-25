from django.urls import path

from modules.authentication import views

urlpatterns = [
    # path("login/", views.MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("register/", views.RegisterView.as_view(), name="auth_register"),
    # path(
    #     "api/activation/<str:token_id>",
    #     views.ActivationView.as_view(),
    #     name="auth_activation",
    # ),
    path("token/", views.TokenView.as_view(), name="default_view"),
]