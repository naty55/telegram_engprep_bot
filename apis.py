from DatabaseAPI import DataBase
from DictAPI import DictAPI
from RamApi import RamApi
from SessionsDict import SessionsDict
from telegram.ext import Updater
import logging


######
# This file is for any object that should be
# accessible from all parts of the program.
# Here will be the factory for all of those objects
######

# API's
db_api = DataBase('test.db')
dict_api = DictAPI('new_dict.csv')
ram_api = RamApi()

# Logging shit goes here
# --- This is not well written - to be fixed in the future ---
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(format_string)
logging.basicConfig(format=format_string, level=logging.INFO)
bot_logger = logging.getLogger('bot_logger')
bot_file_handler = logging.FileHandler('bot_log.log')
print("Test")
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


# Updater
with open("keys.txt", 'r') as f:
    token = f.readline()

updater = Updater(token=token)

