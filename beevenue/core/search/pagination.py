from typing import Generic, List, TypeVar

TItem = TypeVar("TItem")


class Pagination(Generic[TItem]):
    """Generic data structure for a paginated list."""

    def __init__(
        self,
        items: List[TItem],
        page_count: int,
        page_number: int,
        page_size: int,
    ):
        self.items = items
        self.page_count = page_count
        self.page_number = page_number
        self.page_size = page_size

    @staticmethod
    def empty() -> "Pagination[TItem]":
        return Pagination(items=[], page_count=0, page_number=1, page_size=1)

    def __repr__(self) -> str:
        return (
            f"<Pagination {self.page_count=} "
            f"{self.page_number=} {self.page_size=}>"
        )
