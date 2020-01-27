from .base import SearchTerm


class BasicSearchTerm(SearchTerm):
    def __init__(self, term):
        self.term = term

    @classmethod
    def from_match(cls, match):
        return cls(match.group(1))


class NegativeSearchTerm(BasicSearchTerm):
    def __repr__(self):
        return f"-{self.term}"

    def applies_to(self, medium):
        return self.term not in medium.tag_names


class PositiveSearchTerm(BasicSearchTerm):
    def __repr__(self):
        return f"{self.term}"

    def applies_to(self, medium):
        return self.term in medium.tag_names


class RatingSearchTerm(SearchTerm):
    def __init__(self, rating):
        self.rating = rating

    @classmethod
    def from_match(cls, match):
        return RatingSearchTerm(match.group(1))

    def __repr__(self):
        return f"rating:{self.rating}"

    def applies_to(self, medium):
        return medium.rating == self.rating


class Negative(SearchTerm):
    def __init__(self, inner_term):
        self.inner_term = inner_term

    @classmethod
    def from_match(cls, match):
        raise "Unsupported for this SearchTerm"

    def __repr__(self):
        return f"!{self.inner_term.__repr__()}"

    def applies_to(self, medium):
        return not self.inner_term.applies_to(medium)
