import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.connections.models import Connection, Station

print("\nAll Stations:")
print("-" * 50)
for station in Station.objects.all():
    print(f"ID: {station.id}")
    print(f"Name: {station.name}")
    print(f"Code: {station.code}")
    print(f"City: {station.city}")
    print(f"Location: ({station.latitude}, {station.longitude})")
    print("-" * 50)

print("\nAll Connections:")
print("-" * 50)
for conn in Connection.objects.all():
    print(f"ID: {conn.id}")
    print(f"Train Number: {conn.train_number}")
    print(f"From: {conn.departure_station.name} ({conn.departure_station.id})")
    print(f"To: {conn.arrival_station.name} ({conn.arrival_station.id})")
    print(f"Departure: {conn.departure_time}")
    print(f"Arrival: {conn.arrival_time}")
    print(f"Price: {conn.price}")
    print("-" * 50) 