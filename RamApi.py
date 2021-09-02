import json
import urllib.request
import random

class RamApi:
    def __init__(self):
        self.base = "https://rickandmortyapi.com/api/character/"
        self.count = None

    def get_character(self, _id=None):
        if not _id:
            _id = random.randint(0, self.get_count() + 1)
        res = json.load(urllib.request.urlopen(self.base + "/" + str(_id)))
        image = urllib.request.urlopen(res['image']).read()
        name = res['name']
        return name, image

    def get_count(self):
        if not self.count:
            self.count = json.load(urllib.request.urlopen(self.base))['info']['count']
        return self.count
