from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import logging

from modules.trains.trains_service import TrainService
from modules.users.models import Ticket
from modules.users.serializers import TicketSerializer
from modules.users.user_service import UserService

logger = logging.getLogger(__name__)

class TicketView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tickets = user.tickets
        return Response({"content": TicketSerializer(tickets, many=True).data})

    def post(self, request):
        try:
            user = request.user
            logger.info(f"Creating ticket for user: {user.email}")
            
            serializer = TicketSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            if not TrainService().reserve_seat(serializer.validated_data["seat_number"], serializer.validated_data["wagon_number"], serializer.validated_data["train_number"]):
                return Response({"error": "Seat is already reserved"}, status=400)
            
            ticket = serializer.save(user=user)
            return Response({"content": TicketSerializer(ticket).data})
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return Response({"error": str(e)}, status=400)
