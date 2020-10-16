from typing import Generic, List, TypeVar

T = TypeVar("T")


class Pagination(Generic[T]):
    def __init__(
        self, items: List[T], pageCount: int, pageNumber: int, pageSize: int
    ):
        self.items = items
        self.pageCount = pageCount
        self.pageNumber = pageNumber
        self.pageSize = pageSize

    @staticmethod
    def empty() -> "Pagination[T]":
        return Pagination(items=[], pageCount=0, pageNumber=1, pageSize=1)
