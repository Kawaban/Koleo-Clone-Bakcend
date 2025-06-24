from modules.trains.models import Seat
import logging

logger = logging.getLogger(__name__)

class TrainService:
    def reserve_seat(self, seat_number, wagon_number, train_number):
        try:
            seat = Seat.objects.filter(
                seat_number=seat_number,
                wagon__wagon_number=wagon_number,
                wagon__train__number=train_number
            ).first()
            
            logger.info(f"Trying to reserve seat: {seat_number} in wagon: {wagon_number} of train: {train_number}")
            logger.info(f"Found seat: {seat}")
            
            if not seat:
                logger.error(f"Seat not found: {seat_number} in wagon: {wagon_number} of train: {train_number}")
                return False
                
            if not seat.is_available:
                logger.error(f"Seat not available: {seat_number} in wagon: {wagon_number} of train: {train_number}")
                return False
                
            seat.is_available = False
            seat.save()
            return True
            
        except Exception as e:
            logger.error(f"Error reserving seat: {str(e)}")
            return False