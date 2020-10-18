from typing import Callable, Dict, Union

from beevenue import request

from ....models import Medium, Tag

Rateable = Union[Tag, Medium]


class Censorship:
    """Anonymizer of tag names if users aren't allowed to see them."""

    def __init__(
        self, lookup: Dict[int, Rateable], name_func: Callable[[Rateable], str]
    ):
        self.lookup = lookup
        self.name_func = name_func

        context = request.beevenue_context

        self.ratings_to_censor = set(["u"])
        if context.user_role != "admin":
            self.ratings_to_censor.add("e")
        if context.is_sfw:
            self.ratings_to_censor |= set(["q", "e"])

        self.censored_counter = 0
        self.names: Dict[int, str] = dict()

    def get_name(self, tag_id: int) -> str:
        """Get the (potentially anonymized) name of the tag with given id.

        Will return the same name on successive calls with the same id.
        """

        if tag_id not in self.names:
            thing = self.lookup[tag_id]

            if thing.rating in self.ratings_to_censor:
                self.names[tag_id] = f"anon{self.censored_counter}"
                self.censored_counter += 1
            else:
                self.names[tag_id] = self.name_func(thing)

        return self.names[tag_id]
