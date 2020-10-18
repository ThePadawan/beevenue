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

        user_entity = User.query.filter(User.username == username).first()
        user = LoggedInUser(username, user_entity.role)
        return user

    login_manager.user_loader(user_loader)
