from django.shortcuts import render
from requests import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from modules.trains.models import Train, Wagon
from modules.trains.serializers import TrainSerializer
from rest_framework.response import Response


# Create your views here.
class TrainsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, train_number):
        train = Train.objects.get(number=train_number)
        if not train:
            return Response({"error": "Train not found"}, status=404)
        return Response({"content": TrainSerializer(train).data}, status=200)

