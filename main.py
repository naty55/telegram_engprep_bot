from apis import db_api
from bot_functions import (start_handler,
                           button_map_handler,
                           conversation_map_handler,
                           register_handler,
                           quiz_me_handler,
                           quiz_handler,
                           menu_handler)

from telegram.ext import CommandHandler, Updater, CallbackQueryHandler, ConversationHandler, PollAnswerHandler

with open("keys.txt", 'r') as f:
    token = f.readline()

updater = Updater(token=token)
bot = updater.bot

dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start_handler))
dispatcher.add_handler(CommandHandler('register', register_handler))
dispatcher.add_handler(CommandHandler('menu', menu_handler))
dispatcher.add_handler(CallbackQueryHandler(button_map_handler))
dispatcher.add_handler(CommandHandler('quiz_me', quiz_me_handler))
dispatcher.add_handler(PollAnswerHandler(quiz_handler, pass_user_data=True, pass_chat_data=True))
# dispatcher.add_handler(ConversationHandler(conversation_map_handler))
updater.start_polling()
updater.idle()
