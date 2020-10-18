from enum import Enum, unique
from typing import List, Literal, TypedDict, Union


@unique
class _NotificationLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class _NotificationText(TypedDict):
    type: Literal["text"]
    data: str


NotificationLinkData = TypedDict(
    "NotificationLinkData", {"location": str, "text": str}
)


class _NotificationLink(TypedDict):
    type: Literal["link"]
    data: NotificationLinkData


NotificationPart = Union[_NotificationText, _NotificationLink]

Notification = TypedDict(
    "Notification",
    {
        "level": _NotificationLevel,
        "contents": List[NotificationPart],
    },
)


def _text(text: str) -> _NotificationText:
    return {"type": "text", "data": text}


def _link(location: str, text: str) -> _NotificationLink:
    return {"type": "link", "data": {"location": location, "text": text}}


def _make_notification(
    level: _NotificationLevel,
    first_part: NotificationPart,
    *other_parts: NotificationPart,
) -> Notification:
    return {"level": level, "contents": [first_part, *other_parts]}


def simple_error(text: str) -> Notification:
    return _make_notification(_NotificationLevel.ERROR, _text(text))


def simple_warning(text: str) -> Notification:
    return _make_notification(_NotificationLevel.WARNING, _text(text))


def not_sfw() -> Notification:
    return _make_notification(
        _NotificationLevel.INFO,
        _text("Your SFW setting does not allow you to see this."),
    )


def could_not_update_medium() -> Notification:
    return _make_notification(
        _NotificationLevel.ERROR, _text("Could not update medium.")
    )


def no_permission() -> Notification:
    return _make_notification(
        _NotificationLevel.ERROR,
        _text("You do not have the permission to do this."),
    )


def no_such_medium(medium_id: int) -> Notification:
    return _make_notification(
        _NotificationLevel.ERROR,
        _text(f"Could not find medium with ID {medium_id}."),
    )


def no_such_tag(current_name: str) -> Notification:
    return _make_notification(
        _NotificationLevel.ERROR,
        _text(f"Could not find tag with name '{current_name}''."),
    )


def tag_batch_added(added_count: int) -> Notification:
    tag_string = "tag"
    if added_count > 1:
        tag_string = "tags"

    return _make_notification(
        _NotificationLevel.INFO,
        _text(f"Added {added_count} {tag_string} to selected media."),
    )


def new_thumbnail() -> Notification:
    return _make_notification(
        _NotificationLevel.INFO, _text("New thumbnail now available.")
    )


def medium_uploaded(medium_id: int) -> Notification:
    return _make_notification(
        _NotificationLevel.INFO,
        _text("Medium successfully uploaded:"),
        _link(f"/show/{medium_id}", f"{medium_id}"),
    )


def medium_replaced() -> Notification:
    return _make_notification(
        _NotificationLevel.INFO, _text("File successfully replaced.")
    )


def medium_already_exists(filename: str, medium_id: int) -> Notification:
    return _make_notification(
        _NotificationLevel.ERROR,
        _text(f'Cannot handle file "{filename}" since it already exists:'),
        _link(f"/show/{medium_id}", f"Medium {medium_id}"),
    )


def unknown_mime_type(filename: str, mime_type: str) -> Notification:
    return _make_notification(
        _NotificationLevel.ERROR,
        _text(f'Cannot handle file "{filename}" with mime type "{mime_type}".'),
    )
