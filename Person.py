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
        self.interval_to_get_age_is_open = False  # This variable will determine if the bot will get text messages from this person
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
        self.init_competition()
        # time
        self.time = time.time()

    def init_quiz(self):
        """
        Init quiz settings and state
        :return: None
        """
        self.is_on_quiz = False
        self.left_questions = 0
        self.quiz_on_heb_words = False

    def init_competition(self):
        """
        Init competition settings and state
        :return: None
        """
        self.init_quiz()
        self.is_on_competition = False
        self.against = None  # The opponent person

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

    def start_competition(self, other):
        self.start_quiz(False)
        self.is_on_competition = True
        self.finished_competition = False
        self.against = other

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

    def is_busy(self):
        """
        Check if person is on a quiz or competition
        :return: True if person is on quiz or competition; False otherwise
        """
        return self.is_on_quiz or self.is_on_competition

    def get_score(self):
        """
        Return the score of person in the quiz, only if the person didn't finish the quiz already
        :return:
        """
        if self.is_on_quiz:
            return round(((15 - self.failed) / 15) * 100, 2)

    def finish_competition(self):
        if self.is_on_competition:
            self.finished_competition = True

    def close(self):
        db_api.update_last_seen(self.id, self.time)

    def __repr__(self):
        return f"Person name: {self.name}, id: {self.id}, last seen: {self.time}"
