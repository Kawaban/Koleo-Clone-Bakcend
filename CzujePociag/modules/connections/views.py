from django.db import connection
from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

from modules.connections.algorithm import Algorithm
from modules.connections.models import Station
from modules.connections.serializers import ConnectionSearchSerializer, ConnectionResponseSerializer


class ConnectionsView(APIView):
    def post(self, request):
        connection_request = ConnectionSearchSerializer(data=request.data)
        if not connection_request.is_valid():
            return Response(connection_request.errors, status=400)
        result = Algorithm().calculate_path(connection_request.arrival_station, connection_request.departure_station,'t', connection_request.date)
        return Response({"content":ConnectionResponseSerializer(result,many=True)}, status=200)

class StationView(APIView):
    def get(self, request):
        stations = Station.objects.all()
        return Response({"stations": [station.name for station in stations]}, status=200)