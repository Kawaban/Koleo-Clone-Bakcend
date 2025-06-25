from django.shortcuts import render

# Create your views here.
import uuid
from datetime import datetime, timedelta

from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers

# Create your views here.


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework_simplejwt.views import TokenObtainPairView

from config import settings
from modules.authentication.exceptions import ActivationTokenExpiredException
from modules.authentication.models import CustomUser, ActivationToken
from modules.authentication.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    ActivationSerializer,
)
from modules.users.user_service import UserService


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Register",
        description="Register a new user",
        parameters=[
            OpenApiParameter(
                name="email", description="email of new user", required=True, type=str
            ),
            OpenApiParameter(
                name="password",
                description="password of new user",
                required=True,
                type=str,
            ),
        ],
        responses={200: str},  # Define response type
    )
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            auth_user = serializer.create(serializer.validated_data)
            return Response({"content": "User created"}, status=201)
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class ActivationView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Activate account",
        description="Activate account",
        responses={200: str},  # Define response type
    )
    def get(self, request, token_id):
        token = ActivationToken.objects.get(id=token_id)

        if token.expiration_date < datetime.now():
            raise ActivationTokenExpiredException("Activation token expired")

        user = token.user
        user.is_active = True
        user.save()
        return Response({"content": "User activated"})


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            user.delete()
            return Response({"message": "Account deleted successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
