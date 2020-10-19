from beevenue.core.search.base import SearchTerm
from beevenue.core.search.simple import PositiveSearchTerm


def test_terms_are_compared_by_value():
    def term():
        return PositiveSearchTerm("foo")

    x = term()
    y = term()

    are_equal = x == y
    assert are_equal
    assert hash(x) == hash(y)


def test_search_term_abstract_base_method_is_harmless():
    class TestingSearchTerm(SearchTerm):
        @classmethod
        def from_match(cls, match):
            return super().from_match(match)

    TestingSearchTerm.from_match("Foo")
