from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

# Initialize MongoDB client
client = MongoClient(
    st.secrets["mongodb"]["client"]
)
db = client.streamlit_app


def create_user(username, password, email):
    """Create a new user with a hashed password."""
    hashed_password = generate_password_hash(password)
    db.users.insert_one(
        {"username": username, "password": hashed_password, "email": email}
    )


def check_user(username, password):
    """Check if a user exists and the password is correct."""
    user = db.users.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return True
    return False


def book_slot(user, start, end, resourceId):
    """Book a new slot."""
    db.bookings.insert_one(
        {"user": user, "start": start, "end": end, "resourceId": resourceId}
    )
