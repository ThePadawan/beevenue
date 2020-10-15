from flask import request


class Censorship(object):
    def __init__(self, lookup, name_func):
        self.lookup = lookup
        self.name_func = name_func

        context = request.beevenue_context

        self.ratings_to_censor = set(["u"])
        if context.user_role != "admin":
            self.ratings_to_censor.add("e")
        if context.is_sfw:
            self.ratings_to_censor |= set(["q", "e"])

        self.censored_counter = 0
        self.names = dict()

    def get_name(self, id):
        if id not in self.names:
            thing = self.lookup[id]

            if thing.rating in self.ratings_to_censor:
                self.names[id] = f"anon{self.censored_counter}"
                self.censored_counter += 1
            else:
                self.names[id] = self.name_func(thing)

        return self.names[id]
