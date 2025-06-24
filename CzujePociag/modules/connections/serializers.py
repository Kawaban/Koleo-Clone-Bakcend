from rest_framework import serializers


class ConnectionSearchSerializer(serializers.Serializer):
    departure_station = serializers.CharField()
    arrival_station = serializers.CharField()
    time = serializers.CharField(default='00:00:00', required=False, help_text="Format: HH:MM:SS")
    number_of_connections = serializers.IntegerField(default=5, required=False)

class ConnectionResponseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'departure_station': instance.start_stop,
            'arrival_station': instance.end_stop,
            'departure_time': instance.departure_time,
            'arrival_time': instance.arrival_time,
            'duration': str(instance.duration),
            'train_number': instance.train_number,
            'price': str(instance.cost)
        }

class ResultSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "results": [ConnectionResponseSerializer(result).data for result in instance]
        }