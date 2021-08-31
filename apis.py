from DatabaseAPI import DataBase
from DictAPI import DictAPI
import logging
######
# This file is for any object that should be
# accessible from all parts of the program
######
db_api = DataBase('test.db')
dict_api = DictAPI('new_dict.csv')

# Logging shit goes here
# --- This is not well written - to be fixed ---
format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(format_string)
logging.basicConfig(format=format_string, level=logging.INFO)
bot_logger = logging.getLogger('bot_logger')
file_handler = logging.FileHandler('bot_log.log')
file_handler.setFormatter(formatter)
bot_logger.addHandler(file_handler)



