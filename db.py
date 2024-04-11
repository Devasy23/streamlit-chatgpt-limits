import os
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from services import BookingService  # Assuming services.py contains BookingService

# Initialize MongoDB client using environment variable
MONGODB_CLIENT_STRING = os.environ.get('MONGODB_CLIENT_STRING')
client = MongoClient(MONGODB_CLIENT_STRING)
db = client.streamlit_app

# ... (Other code remains unchanged) ...

def book_slot(user, start, end, resourceId):
    """Book a new slot after validating."""
    booking_service = BookingService(db)
    if booking_service.is_valid_booking(user, start, end, resourceId):
        db.bookings.insert_one(
            {"user": user, "start": start, "end": end, "resourceId": resourceId}
        )
        return True
    return False

def edit_booking(booking_id, user, start=None, end=None, resourceId=None):
    """Edit an existing booking."""
    booking_service = BookingService(db)
    return booking_service.edit_booking(booking_id, user, start, end, resourceId)

def delete_booking(booking_id, user):
    """Delete an existing booking."""
    booking_service = BookingService(db)
    return booking_service.delete_booking(booking_id, user)
