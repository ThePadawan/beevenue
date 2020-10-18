from typing import Optional

from ..login_manager import login_manager
from .logged_in_user import LoggedInUser
from .models import User


def init() -> None:
    """Initialize auth component of application."""

    def user_loader(
        username: str,
    ) -> Optional[LoggedInUser]:
        """Try to load user with specified username."""

        maybe_user = User.query.filter(User.username == username).first()

        if not maybe_user:
            return None

        user = LoggedInUser(username, maybe_user.role)
        user.id = username
        return user

    login_manager.user_loader(user_loader)
