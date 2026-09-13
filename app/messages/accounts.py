class AccountMessages:
    REGISTERED_SUCCESSFULLY = "Your account has been created successfully."
    LOGGED_IN_SUCCESSFULLY = "You have logged in successfully."
    LOGGED_OUT_SUCCESSFULLY = "You have been logged out successfully."

    USER_ALREADY_EXISTS = "User already exists!"
    AUTHENTICATION_REQUIRED = "Authentication required"
    INVALID_CREDENTIALS = "Username or password is incorrect!"
    INVALID_TOKEN = "Authentication failed, invalid token"
    TOKEN_EXPIRED = "Token has expired"
    INVALID_TOKEN_TYPE = "Authentication failed, token type is invalid"
    TOKEN_REVOKED = "Token has been revoked"
    USER_ID_NOT_IN_TOKEN = (
        "Authentication failed, user_id is not in token"
    )
    USER_NOT_FOUND = "User not found"
    USER_INACTIVE = "User is inactive"