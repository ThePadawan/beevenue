# These tests are just here to raise coverage the last few percents.
import os
from pathlib import Path

import pytest

from beevenue.beevenue import get_application
from beevenue.core.model import ffmpeg
from beevenue.core.model.search.pagination import Pagination
from beevenue.core.model.search.terms import complex, simple
from beevenue.models import Tag
from beevenue.permissions import _CanSeeMediumWithRatingNeed
from beevenue.spindex.models import SpindexedMedium, SpindexedMediumTagNames
from beevenue.strawberry.rules.common import HasAnyTagsIn, HasRating


def test_permission_need_internals():
    need = _CanSeeMediumWithRatingNeed("q")
    assert not (need == "something else")

    assert len(need.__repr__()) > 0


def test_spindexed_medium_internals():
    medium = SpindexedMedium(
        1,
        "1.0",
        "someHash",
        "mime",
        "q",
        bytes(),
        SpindexedMediumTagNames([], []),
    )
    assert len(medium.__str__()) > 0
    assert len(medium.__repr__()) > 0


def test_tag_cannot_be_created_empty(client):
    assert Tag.create("  ") is None


def test_rules_never_apply_to_nonexistant_media(client):
    def empty_spindex(_):
        class Empty:
            def get_medium(self, medium_id):
                return None

        return Empty()

    with client.app_under_test.test_request_context() as context:
        context.request.spindex = empty_spindex

        assert not HasRating("q").applies_to(1234567)
        assert not HasAnyTagsIn("nonexistantTag").applies_to(1234567)


def test_thumbnailing_weird_mime_type_throws():
    with pytest.raises(Exception):
        ffmpeg.thumbnails("", Path("./"), "application/weird")


def test_app_can_initialize_without_spindex():
    old_env = None
    if "BEEVENUE_SKIP_SPINDEX" in os.environ:
        old_env = os.environ["BEEVENUE_SKIP_SPINDEX"]

    os.environ["BEEVENUE_SKIP_SPINDEX"] = "yep"

    get_application()
    if old_env is None:
        del os.environ["BEEVENUE_SKIP_SPINDEX"]
    else:
        os.environ["BEEVENUE_SKIP_SPINDEX"] = old_env


def test_counting_search_term_internals():
    term = complex.CountingSearchTerm("??", 3)  # invalid operator
    with pytest.raises(Exception):
        term.applies_to(None)


def test_category_search_term_internals():
    term = complex.CategorySearchTerm("c", "??", 3)  # invalid operator

    class FakeMedium:
        def __getattribute__(self, name):
            if name == "tag_names":
                return self
            return set()

    with pytest.raises(Exception):
        term.applies_to(FakeMedium())


def test_negative_search_term_internals():
    with pytest.raises(NotImplementedError):
        simple.Negative.from_match(None)


def test_pagination_internals():
    pagination = Pagination([], 1, 1, 10)
    assert len(pagination.__repr__()) > 0
