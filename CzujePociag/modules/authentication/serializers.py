from rest_framework import serializers
from django.db import IntegrityError
from modules.authentication.models import CustomUser


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        try:
            user = CustomUser.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"]
            )
            return user
        except IntegrityError:
            raise serializers.ValidationError({"email": "User with this email already exists."})


class ActivationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        return token
