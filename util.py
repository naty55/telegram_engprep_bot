from time import sleep, time
from apis import sessions, bot_logger


def clean_old_sessions():
    interval = 30 * 60  # 30 minutes
    while True:
        sleep(interval)
        for i in list(sessions.keys()):
            if time() - sessions[i].time > interval:
                person = sessions.pop(i)
                person.close()
                bot_logger.info("%s session expired id: %s", person.name, person.id)
