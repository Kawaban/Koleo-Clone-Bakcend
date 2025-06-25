from rest_framework import serializers
from datetime import datetime


class ConnectionSearchSerializer(serializers.Serializer):
    departure_station = serializers.CharField()
    arrival_station = serializers.CharField()
    date = serializers.DateField(required=True)
    time = serializers.CharField(default='00:00:00', required=False, help_text="Format: HH:MM:SS")
    number_of_connections = serializers.IntegerField(default=5, required=False)


class ConnectionResponseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'departure_station': instance.departure_station,
            'arrival_station': instance.arrival_station,
            'departure_time': instance.departure_time,
            'arrival_time': instance.arrival_time,
            'duration': str(instance.duration),
            'train_number': instance.train_number,
            'price': str(instance.cost)
        }


class RouteSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # instance is a list of Result objects representing one complete route
        total_price = sum(float(segment.cost) for segment in instance)
        first_segment = instance[0]
        last_segment = instance[-1]
        total_duration = (datetime.strptime(last_segment.arrival_time, "%H:%M:%S") - 
                         datetime.strptime(first_segment.departure_time, "%H:%M:%S")).total_seconds()
        
        return {
            'summary': {
                'departure_station': first_segment.departure_station,
                'arrival_station': last_segment.arrival_station,
                'departure_time': first_segment.departure_time,
                'arrival_time': last_segment.arrival_time,
                'total_duration': str(total_duration),
                'total_price': str(total_price),
                'transfers': len(instance) - 1
            },
            'segments': [ConnectionResponseSerializer(segment).data for segment in instance]
        }


class RoutesResponseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        # instance is a list of routes, where each route is a list of Result objects
        return {
            "routes": [RouteSerializer(route).data for route in instance]
        }