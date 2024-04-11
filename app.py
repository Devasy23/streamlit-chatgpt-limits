from datetime import datetime
import streamlit as st
from dateutil.parser import parse
from streamlit_calendar import calendar

# Importing the necessary modules
from db.connection import users_collection, bookings_collection
import user_management
import booking_management
import booking_service
import user_service
import helpers

# Helper Functions for Authentication
def display_booking_calendar(username):
    # Fetch all bookings from the database
    all_bookings = booking_management.get_all_bookings()

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
        start = parse(slot_details["start"])
        end = parse(slot_details["end"])
        if st.button("Book Slot"):
            if booking_service.is_valid_booking(slot_details["start"], slot_details["end"], all_bookings):
                booking_management.book_slot(username, slot_details["start"], slot_details["end"])
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
            if user_management.check_user(username, password):
                st.session_state["authenticated"] = True
                st.session_state["user"] = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid login.")
    elif mode == "Sign Up":
        email = st.sidebar.text_input("Email")
        if st.sidebar.button("Sign Up"):
            user_management.create_user(username, password, email)
            st.success("Account created successfully! Please log in.")

    if st.session_state.get("authenticated"):
        display_booking_calendar(username=st.session_state["user"])
    else:
        st.warning("Please log in or sign up.")

if __name__ == "__main__":