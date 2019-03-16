from abc import abstractclassmethod, ABCMeta


class SearchTerm(metaclass=ABCMeta):
    @abstractclassmethod
    def from_match(cls, match):
        pass
