from .base import SearchTerm


class BasicSearchTerm(SearchTerm):
    def __init__(self, term, is_quoted):
        self.term = term
        self.is_quoted = is_quoted

    @classmethod
    def from_match(cls, match):
        return cls(
            match.group(1), "\"" in match.group(0))


class NegativeSearchTerm(BasicSearchTerm):
    def __repr__(self):
        return f"-{self.term}"


class PositiveSearchTerm(BasicSearchTerm):
    def __repr__(self):
        return f"{self.term}"


class RatingSearchTerm(SearchTerm):
    def __init__(self, rating):
        self.rating = rating

    @classmethod
    def from_match(cls, match):
        return RatingSearchTerm(match.group(1))

    def __repr__(self):
        return f"rating:{self.rating}"