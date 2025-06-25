from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.trains.trains_service import TrainService
from modules.users.models import Ticket
from modules.users.serializers import TicketSerializer
from modules.users.user_service import UserService


class TicketView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        print("Fetching tickets for user:", request.user.id)

        user = UserService().get_user_by_sub(request.user.id)
        tickets = user.tickets
        return Response({"content": TicketSerializer(tickets, many=True).data})

    def post(self, request):
        user = UserService().get_user_by_sub(request.user.id)
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not TrainService().reserve_seat(serializer.validated_data["seat_number"], serializer.validated_data["wagon_number"], serializer.validated_data["train_number"]):
            return Response({"error": "Seat is already reserved"}, status=400)

        ticket = Ticket.objects.create(
            user=user,
            seat=serializer.validated_data["seat_number"],
            wagon=serializer.validated_data["wagon_number"],
            train_number=serializer.validated_data["train_number"],
            departure_station=serializer.validated_data["departure_station"],
            arrival_station=serializer.validated_data["arrival_station"],
            departure_time=serializer.validated_data["departure_time"],
            arrival_time=serializer.validated_data["arrival_time"],
        )
        return Response({"content": TicketSerializer(ticket).data})
