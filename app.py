from datetime import datetime
import os
import streamlit as st
from dateutil.parser import parse
from pymongo import MongoClient
from streamlit_calendar import calendar
from werkzeug.security import check_password_hash

# Importing the new classes
from models import User, Booking
from services import BookingService

# MongoDB setup (Replace with your connection details)
client = MongoClient(os.getenv('MONGO_CLIENT'))  # Replaced with environment variable
db = client.streamlit_app
users_collection = db.users
bookings_collection = db.bookings

# Instantiate the BookingService
booking_service = BookingService(users_collection, bookings_collection)

# Helper Functions for Authentication
def create_user(username, password, email):
    """Create a new user with a hashed password."""
    user = User(username, password, email)
    user.create(users_collection)

def check_user(username, password):
    """Check if a user exists and the password is correct."""
    return User.verify(username, password, users_collection)

# Main App Logic
def main():
    st.sidebar.title("ChatGPT-4 Query Manager")
    mode = st.sidebar.selectbox("Mode", ["Login", "Sign Up"])

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if mode == "Login":
        if st.sidebar.button("Login"):
            if check_user(username, password):
                st.session_state["authenticated"] = True
                st.session_state["user"] = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid login.")
    elif mode == "Sign Up":
        email = st.sidebar.text_input("Email")
        if st.sidebar.button("Sign Up"):
            create_user(username, password, email)
            st.success("Account created successfully! Please log in.")

    if st.session_state.get("authenticated"):
        display_booking_calendar(username=st.session_state["user"])
    else:
        st.warning("Please log in or sign up.")

def display_booking_calendar(username):
    # Fetch all bookings from the database using the BookingService
    all_bookings = booking_service.get_all_bookings()

    # Convert bookings to calendar events
    events = booking_service.convert_bookings_to_events(all_bookings, username)

    calendar_options = {
        "editable": True,
        "selectable": True,
        "initialView": "timeGridWeek",
        "slotMinTime": "06:00:00",
        "slotMaxTime": "22:00:00",
    }
    calendar_callbacks = ["select"]
    custom_css = """
        .fc-event {
            border: 1px solid #000;
        }
    """

    calendar_result = calendar(
        events=events,
        options=calendar_options,
        callbacks=calendar_callbacks,
        custom_css=custom_css,
    )

    # Handle new bookings
    if "select" in calendar_result:
        slot_details = calendar_result["select"]
        start = parse(slot_details["start"])
        end = parse(slot_details["end"])
        if st.button("Book Slot"):
            try:
                booking_service.book_slot(username, start, end)
                st.success(
                    f"Slot booked from {slot_details['start']} to {slot_details['end']}"
                )
                st.rerun()  # Rerun the app to refresh the view with the new booking
            except Exception as e:
                st.error(str(e))

if __name__ == "__main__":