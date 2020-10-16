from typing import Iterable

from .common import Iff, Then


class Rule(object):
    def __init__(self, iff: Iff, thens: Iterable[Then]):
        if not iff or not thens:
            raise Exception("You must configure one IF and at least one THEN")

        self.iff = iff
        self.thens = thens

    def is_violated_by(self, medium_id: int) -> bool:
        applies = self.iff.applies_to(medium_id)
        if not applies:
            return False

        for then in self.thens:
            if not then.applies_to(medium_id):
                return True

        return False

    def pprint(self) -> str:
        result = f"{self.iff.pprint_if()} "
        result += " and ".join([then.pprint_then() for then in self.thens])
        return result
