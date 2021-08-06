from collections import defaultdict


class SessionsDict(defaultdict):
    """
    dictionary for sessions
    every time a person is being pulled out it will update its time
    """
    def get(self, key):
        person = super(SessionsDict, self).get(key)
        if person:
            person.touch()
        return person
