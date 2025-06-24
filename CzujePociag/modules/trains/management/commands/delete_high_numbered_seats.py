from django.core.management.base import BaseCommand
from modules.trains.models import Seat


class Command(BaseCommand):
    help = 'Deletes all seats with numbers greater than 16'

    def handle(self, *args, **options):
        # Convert seat_number to integer for comparison, filtering out any non-numeric seat numbers
        seats_to_delete = []
        for seat in Seat.objects.all():
            try:
                seat_num = int(seat.seat_number)
                if seat_num > 16:
                    seats_to_delete.append(seat.id)
            except ValueError:
                # Skip seats with non-numeric numbers
                continue

        # Delete the filtered seats
        deletion_count = Seat.objects.filter(id__in=seats_to_delete).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deletion_count} seats with numbers greater than 16'
            )
        ) 