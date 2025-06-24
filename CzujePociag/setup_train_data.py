import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.trains.models import Train, Wagon, Seat
from modules.connections.models import Connection

def setup_train_data():
    # Get unique train numbers from connections
    train_numbers = set(Connection.objects.values_list('train_number', flat=True))
    
    for train_number in train_numbers:
        # Create train if it doesn't exist
        train, created = Train.objects.get_or_create(number=train_number)
        if created:
            print(f"Created train {train_number}")
            
            # Create 3 wagons for each train
            for wagon_num in range(1, 4):
                wagon = Wagon.objects.create(
                    train=train,
                    wagon_number=str(wagon_num)
                )
                print(f"Created wagon {wagon_num} for train {train_number}")
                
                # Create 40 seats for each wagon
                for seat_num in range(1, 41):
                    seat = Seat.objects.create(
                        wagon=wagon,
                        seat_number=str(seat_num),
                        is_available=True
                    )
                print(f"Created 40 seats for wagon {wagon_num}")

if __name__ == '__main__':
    setup_train_data() 