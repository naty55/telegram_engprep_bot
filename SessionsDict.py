from collections import defaultdict


class SessionsDict(defaultdict):

    def get(self, key):
        person = super(SessionsDict, self).get(key)
        if person:
            person.touch()
        return person
