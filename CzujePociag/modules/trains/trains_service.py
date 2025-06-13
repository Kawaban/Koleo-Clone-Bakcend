from modules.trains.models import Seat


class TrainService:
    def reserve_seat(self, seat_number, wagon_number, train_number):
        seat = Seat.objects.filter(
            seat_number=seat_number,
            wagon__wagon_number=wagon_number,
            wagon__train__number=train_number
        ).first()
        if not seat:
            return False
        if not seat.is_available:
            return False
        seat.is_available = False
        seat.save()
        return True