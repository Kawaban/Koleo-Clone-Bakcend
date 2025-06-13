from django.db import models

from modules.core.models import BaseModel


# Create your models here.

class Station(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.code})"

class Connection(BaseModel):
    train_number = models.CharField(max_length=20)

    departure_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='departures')
    arrival_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='arrivals')

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.train_number} from {self.departure_station} to {self.arrival_station}"

