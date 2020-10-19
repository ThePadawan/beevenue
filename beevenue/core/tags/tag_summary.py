from typing import List, TypedDict

TagSummaryEntry = TypedDict(
    "TagSummaryEntry",
    {
        "tag": str,
        "rating": str,
        "implied_by_something": bool,
        "media_count": int,
    },
)


class TagSummary:
    """Viewmodel to hold data for short tag summary."""

    def __init__(self, tags: List[TagSummaryEntry]):
        self.tags = tags
