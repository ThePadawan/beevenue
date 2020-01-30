import pytest

from beevenue.strawberry.rules.rule import Rule
from beevenue.strawberry.rules.common import HasRating
from beevenue.strawberry.rules.then import Fail


def test_rule_must_have_iff():
    with pytest.raises(Exception):
        Rule(None, [Fail()])


def test_rule_must_have_thens():
    with pytest.raises(Exception):
        Rule(HasRating("u"), [])
