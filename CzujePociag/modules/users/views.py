from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from modules.trains.trains_service import TrainService
from modules.users.serializers import TicketSerializer
from modules.users.user_service import UserService


class TicketView(APIView):
    def get(self, request):
        user = UserService().get_user_by_email(request.user.email)
        tickets = user.tickets
        return Response({"content": TicketSerializer(tickets, many=True).data})

    def post(self, request):
        user = UserService().get_user_by_email(request.user.email)
        serializer = TicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not TrainService().reserve_seat(serializer.validated_data["seat_number"], serializer.validated_data["wagon_number"], serializer.validated_data["train_number"]):
            return Response({"error": "Seat is already reserved"}, status=400)
        ticket = serializer.save(user=user)
        return Response({"content": TicketSerializer(ticket).data})
