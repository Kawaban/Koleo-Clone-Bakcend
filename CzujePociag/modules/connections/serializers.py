from rest_framework import serializers


class ConnectionSearchSerializer(serializers.Serializer):
    departure_station = serializers.CharField()
    arrival_station = serializers.CharField()
    date = serializers.DateField()

class ConnectionResponseSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'departure_station': instance.departure_station,
            'arrival_station': instance.arrival_station,
            'departure_time': instance.departure_time.isoformat(),
            'arrival_time': instance.arrival_time.isoformat(),
            'duration': str(instance.duration),
            'train_number': instance.train_number,
            'price': str(instance.price)
        }