from abc import abstractclassmethod, ABCMeta


class SearchTerm(metaclass=ABCMeta):
    @abstractclassmethod
    def from_match(cls, match):
        pass

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(self.__repr__())
