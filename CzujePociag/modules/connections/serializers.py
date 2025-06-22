from rest_framework import serializers


class ConnectionSearchSerializer(serializers.Serializer):
    departure_station = serializers.CharField()
    arrival_station = serializers.CharField()
    date = serializers.DateField()

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