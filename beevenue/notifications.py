from enum import Enum, unique

from flask import jsonify


@unique
class NotificationLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


def _text(t):
    return {"type": "text", "data": t}


def _link(location, text):
    return {"type": "link", "data": {"location": location, "text": text}}


def _make_notification(level, first_part, *other_parts):
    return jsonify({'level': level, 'contents': [first_part, *other_parts]})


def simple_error(text):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(text))


def not_sfw():
    return _make_notification(
        NotificationLevel.INFO,
        _text(f"Your SFW setting does not allow you to see this."))


def could_not_update_medium():
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"Could not update medium."))


def no_permission():
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"You do not have the permission to do this."))


def no_such_medium(medium_id):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"Could not find medium with ID {medium_id}."))


def no_such_tag(current_name):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"Could not find tag with name '{current_name}''."))


def tag_renamed():
    return _make_notification(
        NotificationLevel.INFO,
        _text(f"Successfully renamed tag."))


def medium_uploaded(medium_id):
    return _make_notification(
        NotificationLevel.INFO,
        _text(f"Medium successfully uploaded:"),
        _link(f'/show/{medium_id}', f"{medium_id}"))


def medium_already_exists(medium_id):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"Medium already exists:"),
        _link(f'/show/{medium_id}', f"{medium_id}"))
