from apis import dict_api, db_api
import time


class Person:
    """
    Represent live session with the bot
    """

    def __init__(self, telegram_chat_id, current_name):
        """
        :param telegram_chat_id:
        :param current_name:
        """
        self.telegram_chat_id = telegram_chat_id
        self.current_name = current_name
        self._initialize()

    def _initialize(self):
        person_data = db_api.get_person_data(self.telegram_chat_id)
        if person_data:
            self.is_known = True
            self.name = person_data['name']
            self.gender = person_data['gender']
        else:
            self.name = self.current_name
            self.is_known = False
        self.touch()

    def save_person_data(self):
        db_api.add_new_person(self.name, self.telegram_chat_id)

    def read_person_data(self):
        """
        Not Implemented yet; should deal with more complex data if needed in the future
        :return:
        """
        pass

    def touch(self):
        """
        Update last time this person was in touch with the bot
        (used to make sure the bot won't be overflooded by persons that are out of session)
        :return: None
        """
        self.time = time.time()
