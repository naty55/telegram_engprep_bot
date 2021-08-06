from apis import db_api
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
        self.id = telegram_chat_id
        self.current_name = current_name
        self.name = current_name
        self.is_known = False
        self.interval_to_get_age_is_open = False  # This variable would determine if the bot will get text messages from this person
        self._initialize()

    def _initialize(self):
        """
        Initialize person settings
        :return:
        """
        person_data = db_api.get_person_data(self.id)
        if person_data:
            self.is_known = True
            self.name = person_data['name']
            self.gender = person_data['gender']
        self.init_quiz()
        # time
        self.time = time.time()

    def init_quiz(self):
        """
        Init quiz settings
        :return:
        """
        self.is_on_quiz = False
        self.left_questions = 0
        self.quiz_on_heb_words = False

    def start_quiz(self, on_heb_words):
        """
        start quiz - adjust settings for the quiz
        :param on_heb_words: boolean flag to determine if the quiz is on hebrew or english words
        :return:
        """
        self.is_on_quiz = True
        self.left_questions = 15
        self.failed = 15
        self.quiz_on_heb_words = on_heb_words

    def save_person_data(self):
        """
        Save person data in db
        :return:
        """
        # This method might be edited in future in order to
        # also let users to update their details
        db_api.add_new_person(self.name, self.id, self.gender, self.age)
        self.is_known = True

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
