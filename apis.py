from DatabaseAPI import DataBase
from DictAPI import DictAPI
from SessionsDict import SessionsDict
from telegram.ext import Updater
import logging
import json

######
# This file is for any object that should be
# accessible from all parts of the program.
# Here will be the factory for all of those objects
######

# API's
db_api = DataBase('test.db')
dict_api = DictAPI('new_dict.csv')

# Logging shit goes here
# --- This is not well written - to be fixed in the future ---
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(format_string)
logging.basicConfig(format=format_string, level=logging.INFO)
bot_logger = logging.getLogger('bot_logger')
bot_file_handler = logging.FileHandler('bot_log.log')
bot_file_handler.setFormatter(formatter)
bot_logger.addHandler(bot_file_handler)

# Sessions object
sessions = SessionsDict(lambda: False)

# Message Logger
message_logger = logging.getLogger("MessageLogger")
message_logger.propagate = False
message_file_handler = logging.FileHandler('messages.log')
message_file_handler.setFormatter(formatter)
message_logger.addHandler(message_file_handler)


# Configuration
with open('config.json', 'r') as c:
    config = json.load(c)


updater = Updater(token=config['token'])

