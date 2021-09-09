import sys
from threading import Thread
from apis import updater
from bot_handlers import notify_all_users, clean_old_sessions


if __name__ == '__main__':
    if len(sys.argv) > 1:
        notify_all_users(sys.argv[1], updater.bot)

    Thread(target=clean_old_sessions).start()

    updater.start_polling()
    updater.idle()

