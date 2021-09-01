from bot_functions import (start_handler,
                           button_map_handler,
                           register_handler,
                           quiz_me_handler,
                           quiz_me_he_handler,
                           quiz_me_en_handler,
                           quiz_handler,
                           menu_handler,
                           age_handler,
                           contact_handler,
                           notify_all_users
                           )
import sys
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler, PollAnswerHandler, MessageHandler, Filters

with open("keys.txt", 'r') as f:
    token = f.readline()

updater = Updater(token=token)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('register', register_handler))
dispatcher.add_handler(CommandHandler('menu', menu_handler))
dispatcher.add_handler(CommandHandler('contact', contact_handler))
dispatcher.add_handler(CommandHandler('quiz_me', quiz_me_handler))
dispatcher.add_handler(CommandHandler('quiz_me_en', quiz_me_en_handler))
dispatcher.add_handler(CommandHandler('quiz_me_he', quiz_me_he_handler))
dispatcher.add_handler(CallbackQueryHandler(button_map_handler))
dispatcher.add_handler(PollAnswerHandler(quiz_handler, pass_user_data=True, pass_chat_data=True))
dispatcher.add_handler(MessageHandler(Filters.regex("^[1-9][0 -9]*$"), age_handler))

if len(sys.argv) > 1:
    notify_all_users(sys.argv[1], updater.bot)


updater.start_polling()
updater.idle()
