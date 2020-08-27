from enum import Enum, unique


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
    return {"level": level, "contents": [first_part, *other_parts]}


def simple_error(text):
    return _make_notification(NotificationLevel.ERROR, _text(text))


def simple_warning(text):
    return _make_notification(NotificationLevel.WARNING, _text(text))


def not_sfw():
    return _make_notification(
        NotificationLevel.INFO,
        _text("Your SFW setting does not allow you to see this."),
    )


def could_not_update_medium():
    return _make_notification(
        NotificationLevel.ERROR, _text("Could not update medium.")
    )


def no_permission():
    return _make_notification(
        NotificationLevel.ERROR,
        _text("You do not have the permission to do this."),
    )


def no_such_medium(medium_id):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"Could not find medium with ID {medium_id}."),
    )


def no_such_tag(current_name):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f"Could not find tag with name '{current_name}''."),
    )


def tag_batch_added(tag_count, added_count):
    tag_string = "tag"
    if tag_count > 1:
        tag_string = "tags"

    return _make_notification(
        NotificationLevel.INFO,
        _text(f"Added {added_count} {tag_string} to selected media."),
    )


def new_thumbnail():
    return _make_notification(
        NotificationLevel.INFO, _text("New thumbnail now available.")
    )


def medium_uploaded(medium_id):
    return _make_notification(
        NotificationLevel.INFO,
        _text("Medium successfully uploaded:"),
        _link(f"/show/{medium_id}", f"{medium_id}"),
    )


def medium_already_exists(filename, medium_id):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f'Cannot handle file "{filename}" since it already exists:'),
        _link(f"/show/{medium_id}", f"Medium {medium_id}"),
    )


def unknown_mime_type(filename, mime_type):
    return _make_notification(
        NotificationLevel.ERROR,
        _text(f'Cannot handle file "{filename}" with mime type "{mime_type}".'),
    )
