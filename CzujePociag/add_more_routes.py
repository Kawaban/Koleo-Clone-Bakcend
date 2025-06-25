import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.connections.models import Connection, Station

# Helper function to create a connection
def create_connection(train_number, departure_station, arrival_station, departure_time, arrival_time, price):
    Connection.objects.create(
        train_number=train_number,
        departure_station=departure_station,
        arrival_station=arrival_station,
        departure_time=departure_time,
        arrival_time=arrival_time,
        price=price
    )

# Get station objects
warszawa = Station.objects.get(code='WAW')
krakow = Station.objects.get(code='KRK')
gdansk = Station.objects.get(code='GDA')
poznan = Station.objects.get(code='POZ')
wroclaw = Station.objects.get(code='WRO')

# Base date for all connections
base_date = timezone.make_aware(datetime(2025, 6, 20))

# New alternative routes

# 1. Gdańsk -> Warszawa (through Poznań)
create_connection(
    'IC 7701',
    gdansk, poznan,
    base_date + timedelta(hours=7),  # 07:00
    base_date + timedelta(hours=10, minutes=30),  # 10:30
    79.99
)

create_connection(
    'IC 7702',
    poznan, warszawa,
    base_date + timedelta(hours=11),  # 11:00
    base_date + timedelta(hours=14),  # 14:00
    69.99
)

# 2. Kraków -> Warszawa (through Wrocław)
create_connection(
    'IC 8801',
    krakow, wroclaw,
    base_date + timedelta(hours=8),  # 08:00
    base_date + timedelta(hours=11, minutes=30),  # 11:30
    89.99
)

create_connection(
    'IC 8802',
    wroclaw, warszawa,
    base_date + timedelta(hours=12),  # 12:00
    base_date + timedelta(hours=16),  # 16:00
    99.99
)

# 3. Gdańsk -> Kraków (through Poznań)
create_connection(
    'IC 9901',
    gdansk, poznan,
    base_date + timedelta(hours=6),  # 06:00
    base_date + timedelta(hours=9, minutes=30),  # 09:30
    89.99
)

create_connection(
    'IC 9902',
    poznan, krakow,
    base_date + timedelta(hours=10),  # 10:00
    base_date + timedelta(hours=14, minutes=30),  # 14:30
    109.99
)

# 4. Wrocław -> Gdańsk (through Poznań, different timing than existing route)
create_connection(
    'IC 1101',
    wroclaw, poznan,
    base_date + timedelta(hours=7),  # 07:00
    base_date + timedelta(hours=9, minutes=15),  # 09:15
    59.99
)

create_connection(
    'IC 1102',
    poznan, gdansk,
    base_date + timedelta(hours=10),  # 10:00
    base_date + timedelta(hours=13, minutes=30),  # 13:30
    89.99
)

print("Added new alternative routes with the following paths:")
print("1. Gdańsk -> Poznań -> Warszawa")
print("2. Kraków -> Wrocław -> Warszawa")
print("3. Gdańsk -> Poznań -> Kraków")
print("4. Wrocław -> Poznań -> Gdańsk") 