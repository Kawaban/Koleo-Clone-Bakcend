import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.connections.models import Connection, Station

# Get the stations
warszawa = Station.objects.get(name="Warszawa Centralna")
krakow = Station.objects.get(name="Kraków Główny")

print("\nDirect connections from Warszawa to Kraków:")
print("-" * 70)
direct_connections = Connection.objects.filter(
    departure_station=warszawa,
    arrival_station=krakow
)
for conn in direct_connections:
    print(f"Train: {conn.train_number}")
    print(f"Departure: {conn.departure_time}")
    print(f"Arrival: {conn.arrival_time}")
    print(f"Price: {conn.price} PLN")
    print("-" * 30)

print("\nPossible intermediate stations:")
print("-" * 70)
# Find all stations that can be reached from Warszawa
from_warszawa = Connection.objects.filter(departure_station=warszawa).values_list('arrival_station__name', flat=True).distinct()
# Find all stations that can reach Kraków
to_krakow = Connection.objects.filter(arrival_station=krakow).values_list('departure_station__name', flat=True).distinct()
# Find common stations (potential intermediate stops)
intermediate = set(from_warszawa).intersection(set(to_krakow))

print("Possible intermediate stations:", list(intermediate))

print("\nPotential indirect routes:")
print("-" * 70)
for station in intermediate:
    print(f"\nVia {station}:")
    print("-" * 30)
    # First leg
    first_leg = Connection.objects.filter(
        departure_station=warszawa,
        arrival_station__name=station
    )
    # Second leg
    second_leg = Connection.objects.filter(
        departure_station__name=station,
        arrival_station=krakow
    )
    
    for first in first_leg:
        for second in second_leg:
            if first.arrival_time < second.departure_time:
                print(f"Route option:")
                print(f"1. {first.train_number}: {first.departure_time} -> {first.arrival_time} ({first.price} PLN)")
                print(f"2. {second.train_number}: {second.departure_time} -> {second.arrival_time} ({second.price} PLN)")
                print(f"Total price: {first.price + second.price} PLN")
                print("-" * 30) 