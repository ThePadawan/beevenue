
class Rule(object):
    def __init__(self, iff, thens):
        if not iff or not thens:
            raise Exception("You must configure one IF and at least one THEN")

        self.iff = iff
        self.thens = thens

    def pprint(self):
        result = ''
        result += self.iff.pprint_if()
        result += ' '
        result += ' and '.join([then.pprint_then() for then in self.thens])
        return result
