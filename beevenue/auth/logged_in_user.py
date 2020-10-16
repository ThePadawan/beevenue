from flask_login import UserMixin


class LoggedInUser(UserMixin):
    def __init__(self, id: str, role: str):
        self.id = id
        self.role = role
