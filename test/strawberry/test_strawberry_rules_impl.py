import pytest

from beevenue.strawberry.common import (
    HasAnyTagsIn,
    HasAnyTagsLike,
    HasRating,
)
from beevenue.strawberry.iff import All
from beevenue.strawberry.json import RuleEncoder, RulePartEncoder
from beevenue.strawberry.rule import Rule
from beevenue.strawberry.then import Fail

rules = [
    Rule(HasRating("u"), [Fail()]),
    Rule(HasRating(), [HasAnyTagsLike("x:.*")]),
    Rule(HasAnyTagsLike("x:.*"), [HasRating("q")]),
    Rule(HasAnyTagsIn("forbidden"), [HasAnyTagsIn("knowledge")]),
    Rule(All(), [HasRating()]),
]


def test_rule_must_have_iff():
    with pytest.raises(Exception):
        Rule(None, [Fail()])


def test_rule_must_have_thens():
    with pytest.raises(Exception):
        Rule(HasRating("u"), [])


def test_hasanytagslike_must_have_regexes():
    with pytest.raises(Exception):
        HasAnyTagsLike()


def test_hasanytagsin_must_have_tags():
    with pytest.raises(Exception):
        HasAnyTagsIn()


def test_fail_applies_to_nothing():
    assert not Fail().applies_to(42)


def test_fail_never_has_medium_ids():
    assert not Fail().get_medium_ids()


@pytest.mark.parametrize("rule", rules)
def test_pprint_normal_case(rule):
    printed = rule.pprint()
    assert len(printed) > 0


def test_rule_part_encoder_throws_on_unknown():
    with pytest.raises(Exception):
        RulePartEncoder().default("")


def test_rule_encoder_throws_on_unknown():
    with pytest.raises(Exception):
        RuleEncoder().default("")
