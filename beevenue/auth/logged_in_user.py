from flask_login import UserMixin


class LoggedInUser(UserMixin):
    """Data structure representing a logged in user."""

    def __init__(self, user_id: str, role: str):
        self.id = user_id  # pylint: disable=invalid-name
        self.role = role
