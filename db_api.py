import sqlite3
from sqlite3 import Error


def neat_word(word):
    """
    Generic function to neat a string to keep the words stored in the DB in one manner
    :param word: word to neat
    :return: striped lowered case word
    """
    return word.strip().lower()


class DataBase:
    """
    """

    def __init__(self, filename):
        """
        Initialize the connection to DB
        :param filename:
        """
        self.connection = None
        self.create_connection(filename)
        self.initialize_tables()

    def create_connection(self, filename):
        """
        Connect to DB
        :param filename:
        :return:
        """
        conn = None
        try:
            conn = sqlite3.connect(filename)
            print("[INFO] connection to DB successful")
        except Error as e:
            print(f"[ERROR] error {e}")
        self.connection = conn

    def initialize_tables(self):
        dict_table = "CREATE TABLE IF NOT EXISTS dict (" \
                     "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                     "word TEXT," \
                     "translation TEXT );"

        persons_table = "CREATE TABLE IF NOT EXISTS persons (" \
                        "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                        "name TEXT," \
                        "telegram_id INTEGER," \
                        "age INTEGER, " \
                        "gender INTEGER," \
                        "dict_index INTEGER );"

        scores_table = "CREATE TABLE IF NOT EXISTS scores (" \
                       "word_id INTEGER NOT NULL," \
                       "person_id INTEGER NOT NULL," \
                       "duration INTEGER NOT NULL," \
                       "failures INTEGER NOT NULL, " \
                       "total INTEGER NOT NULL, " \
                       "FOREIGN KEY (word_id) REFERENCES dict(id) " \
                       "FOREIGN KEY (person_id) REFERENCES persons(id) );"

        success = self.exec_query(dict_table) + self.exec_query(persons_table) + self.exec_query(scores_table)
        if success == 0:
            print("[INFO] Tables are all set")

    def exec_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            return 0
        except Error as e:
            print(f"[ERROR] The error {e} occurred")
            return 1

    def exec_read_query(self, query):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"[ERROR] The error {e} occurred")
            return []

    def check_for_person_or_word(self, table, conditions):
        query = "SELECT "

    def add_new_word(self, word, translation):
        word = neat_word(word)
        translation = neat_word(translation)

        result = self.exec_read_query(f"SELECT translation FROM dict WHERE word = '{word}'")
        exists = result != []

        if exists:
            e_translations = result[0][0].split(",")
            if translation not in e_translations:
                e_translations.append(translation)
            e_translations = ",".join(e_translations)
            query = f"""
                    UPDATE
                        dict
                    SET
                        translation = '{e_translations}'
                    WHERE
                        word = '{word}'
                    """

        else:
            query = f"""
                    INSERT INTO 
                        dict (word, translation)
                    VALUES
                        ('{word}','{translation}');
                    """
        success = self.exec_query(query)
        if success == 0:
            print(f"[INFO] the word {word} and its translation {translation} are all set")

    def delete_word(self, word):
        delete_query = f"DELETE FROM dict WHERE word = '{neat_word(word)}'"
        success = self.exec_query(delete_query)
        if success == 0:
            print(f"[INFO] The word {word} had been successfully deleted")

    def get_translation(self, word):
        """
        Get a translation for a word from the DB
        :param word: word to get the translation for
        :return: the translation if the word is in the DB; otherwise return empty string
        """
        result = self.exec_read_query(f"SELECT translation FROM dict WHERE word = '{neat_word(word)}'")
        if result:
            return result[0][0]
        return ""


