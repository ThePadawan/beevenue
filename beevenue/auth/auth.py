
from ..login_manager import login_manager
from .logged_in_user import LoggedInUser
from .models import User


@login_manager.user_loader
def user_loader(username):
    maybe_user = User.query.filter(User.username == username).first()

    if not maybe_user:
        return

    user = LoggedInUser(username, maybe_user.role)
    user.id = username
    return user
