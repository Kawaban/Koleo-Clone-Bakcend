from django.db import models

from modules.core.models import BaseModel


class Train(BaseModel):
    number = models.CharField(max_length=20, unique=True)

class Wagon(BaseModel):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='wagons')
    wagon_number = models.CharField(max_length=10)


class Seat(BaseModel):
    wagon = models.ForeignKey(Wagon, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
