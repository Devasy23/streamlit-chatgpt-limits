from user_management import check_user

def authenticate_user(username, password):
    # Implementation for user authentication using user_management functions
    if check_user(username, password):
        return True
    else: