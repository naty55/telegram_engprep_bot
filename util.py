from time import sleep, time
from apis import sessions, bot_logger
import json
import urllib.request
import os
import random


def clean_old_sessions():
    interval = 30 * 60  # 30 minutes
    while True:
        sleep(interval)
        for i in list(sessions.keys()):
            if time() - sessions[i].time > interval:
                person = sessions.pop(i)
                person.close()
                bot_logger.info("%s session expired id: %s", person.name, person.id)


def get_ram_mem(_id=None):
    os.environ['no_proxy'] = "https://rickandmortyapi.com"
    base_url = "https://rickandmortyapi.com/api/character/"
    count = json.load(urllib.request.urlopen(base_url))['info']['count']
    if not _id:
        _id = random.randint(0, count + 1)
    res = json.load(urllib.request.urlopen(base_url + "/" + str(_id)))
    image = urllib.request.urlopen(res['image']).read()
    name = res['name']
    return name, image
