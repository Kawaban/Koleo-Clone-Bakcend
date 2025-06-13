from rest_framework import serializers

class SeatSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'seat_number': instance.seat_number,
            'is_available': instance.is_available
        }

class WagonSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'wagon_number': instance.wagon_number,
            'seats': SeatSerializer(instance.seats.all(), many=True).data
        }

class TrainSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'number': instance.number,
            'wagons': WagonSerializer(instance.wagons.all(), many=True).data
        }
