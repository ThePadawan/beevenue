
import bcrypt

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


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')

    maybe_user = User.query.filter(User.username == username).first()

    if not maybe_user:
        return

    user = LoggedInUser(username, maybe_user.role)

    user.is_authenticated = bcrypt.checkpw(
        request.form['password'], maybe_user.hash)

    return user
