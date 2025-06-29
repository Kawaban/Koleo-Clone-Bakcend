from django.db import connection
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from datetime import datetime

from modules.connections.algorithm import Algorithm, Result
from modules.connections.models import Station
from modules.connections.serializers import ConnectionSearchSerializer, RoutesResponseSerializer


class ConnectionsView(APIView):
    permission_classes = (AllowAny,)  # Allow unauthenticated access
    
    def post(self, request):
        connection_request = ConnectionSearchSerializer(data=request.data)
        if not connection_request.is_valid():
            return Response(connection_request.errors, status=400)
            
        validated_data = connection_request.validated_data
        print("validated_data: ", validated_data)
        
        # Convert date to time string starting at midnight
        start_time = datetime.combine(validated_data['date'], datetime.min.time()).strftime("%H:%M:%S")
        
        results = Algorithm().calculate_path(
            validated_data['departure_station'],
            validated_data['arrival_station'],
            't',
            start_time,
            n_paths=validated_data.get('number_of_connections', 5)
        )
        print("Results:", results)
        
        return Response(RoutesResponseSerializer(results).data, status=200)


class StationView(APIView):
    permission_classes = (AllowAny,)  # Allow unauthenticated access
    
    def get(self, request):
        stations = Station.objects.all()
        return Response({"stations": [station.name for station in stations]}, status=200)