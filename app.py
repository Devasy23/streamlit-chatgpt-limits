from datetime import datetime, timedelta

import streamlit as st
# import toml
from dateutil.parser import parse
from pymongo import MongoClient
from streamlit_calendar import calendar
from werkzeug.security import check_password_hash, generate_password_hash

# config = toml.load("config.toml")
# MongoDB setup (Replace with your connection details)
client = MongoClient(st.secrets["mongodb"]["client"])
db = client.streamlit_app
users_collection = db.users
bookings_collection = db.bookings


# Helper Functions for Authentication
def create_user(username, password, email):
    """Create a new user with a hashed password."""
    hashed_password = generate_password_hash(password)
    users_collection.insert_one(
        {"username": username, "password": hashed_password, "email": email}
    )


def check_user(username, password):
    """Check if a user exists and the password is correct."""
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user["password"], password):
        return True
    return False


def book_slot(username, start, end):
    bookings_collection.insert_one({"user": username, "start": start, "end": end})


def get_all_bookings():
    """Retrieve all bookings."""
    return list(bookings_collection.find({}, {"_id": 0}))


def is_slot_available(start, end, booked_slots):
    # Make start and end offset-naive
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)

    # Check if the slot is in the future
    if start < datetime.now():
        return False

    # Check if the slot overlaps with any booked slot
    for booked_slot in booked_slots:
        booked_start = parse(booked_slot["start"]).replace(tzinfo=None)
        booked_end = parse(booked_slot["end"]).replace(tzinfo=None)
        if max(start, booked_start) < min(end, booked_end):
            return False

    return True


def verify_slot_length(start, end):
    # minimum slot length of 3 hour
    start = datetime.strptime(start, "%Y-%m-%dT%H:%M:%S.%fZ")
    end = datetime.strptime(end, "%Y-%m-%dT%H:%M:%S.%fZ")

    slot_length = timedelta.total_seconds(end - start)
    print(slot_length)
    if slot_length >= 3600 * 3:
        return True
    return False


def display_booking_calendar(username):
    # Fetch all bookings from the database
    all_bookings = get_all_bookings()

    # Convert bookings to calendar events
    events = [
        {
            "title": f"Booked by {booking['user']}",
            "start": booking["start"],
            "end": booking["end"],
            "color": (
                "#FF5733" if booking["user"] == username else "#338AFF"
            ),  # Different color for the current user's bookings
        }
        for booking in all_bookings
    ]

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
        start = datetime.strptime(slot_details["start"], "%Y-%m-%dT%H:%M:%S.%fZ")
        end = datetime.strptime(slot_details["end"], "%Y-%m-%dT%H:%M:%S.%fZ")
        if st.button("Book Slot"):
            if verify_slot_length(
                slot_details["start"], slot_details["end"]
            ) and is_slot_available(start, end, all_bookings):
                book_slot(username, slot_details["start"], slot_details["end"])
                st.success(
                    f"Slot booked from {slot_details['start']} to {slot_details['end']}"
                )
                st.rerun()  # Rerun the app to refresh the view with the new booking
            else:
                st.error(
                    "Slot length should be minimum 3 hours or Slot is already booked. Please select another slot."
                )


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


if __name__ == "__main__":
    main()
