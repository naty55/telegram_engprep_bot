import sys
from threading import Thread
from apis import updater
from util import clean_old_sessions
from bot_functions import notify_all_users
import bot_handlers # This is not importing for nothing, if you don't import the handlers won't be registered in the dispatcher; should be fixed in future


if __name__ == '__main__':
    if len(sys.argv) > 1:
        notify_all_users(sys.argv[1], updater.bot)

    Thread(target=clean_old_sessions).start()
    updater.start_polling()
    updater.idle()

