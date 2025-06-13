from django.db import models

from modules.core.models import BaseModel


# Create your models here.

class User(BaseModel):
    email = models.EmailField(unique=True)

class Ticket(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    seat = models.CharField(max_length=10)
    wagon = models.CharField(max_length=10)
    train_number = models.CharField(max_length=20)
    departure_station = models.CharField(max_length=100)
    arrival_station = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

