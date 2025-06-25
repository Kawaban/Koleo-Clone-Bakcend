from django.db import connection
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response

from modules.connections.algorithm import Algorithm, Result
from modules.connections.models import Station
from modules.connections.serializers import ConnectionSearchSerializer, ConnectionResponseSerializer, ResultSerializer


class ConnectionsView(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        connection_request = ConnectionSearchSerializer(data=request.data)
        if not connection_request.is_valid():
            return Response(connection_request.errors, status=400)
        result = Algorithm().calculate_path(connection_request.validated_data['departure_station'],connection_request.validated_data['arrival_station'],'t',n_paths=connection_request.validated_data.get('number_of_connections', 5),start_time= connection_request.validated_data.get('time', '00:00:00'))
        print(result)
        return Response({"content":ResultSerializer(result,many=True).data}, status=200)

class StationView(APIView):
    permission_classes = (AllowAny,)
    def get(self, request):
        stations = Station.objects.all()
        return Response({"stations": [station.name for station in stations]}, status=200)