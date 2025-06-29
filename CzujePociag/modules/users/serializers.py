from rest_framework import serializers

from modules.users.models import Ticket


class TicketSerializer(serializers.Serializer):
    seat_number = serializers.CharField()
    wagon_number = serializers.CharField()
    train_number = serializers.CharField()
    departure_station = serializers.CharField()
    arrival_station = serializers.CharField()
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        if not user:
            raise serializers.ValidationError("User is required to create a ticket")
            
        return Ticket.objects.create(
            user=user,
            seat=validated_data["seat_number"],
            wagon=validated_data["wagon_number"],
            train_number=validated_data["train_number"],
            departure_station=validated_data["departure_station"],
            arrival_station=validated_data["arrival_station"],
            departure_time=validated_data["departure_time"],
            arrival_time=validated_data["arrival_time"],
        )

    def to_representation(self, instance):
        return {
            'seat_number': instance.seat,
            'wagon_number': instance.wagon,
            'train_number': instance.train_number,
            'departure_station': instance.departure_station,
            'arrival_station': instance.arrival_station,
            'departure_time': instance.departure_time.isoformat(),
            'arrival_time': instance.arrival_time.isoformat(),
        }


