import sqlite3
from sqlite3 import Error


class DataBase:
    """
    This class represent the API for the DataBase that is actually a dictionary.
    The DB has only one table that has 4 columns, the first for ID,
    the second for the word, the third for the translation of this word,
    and the forth is for the rate of error you have,
    -1 if you have never been tested on that word;
    0 if you have been tested and got the answer right;
    1 or higher the times you have tested and sadly you got the wrong answer;

    The API providing the following commands:

    Push: push new word and its translation
    Get: get the translations for a word
    Update: update the translation for an existing word
    Delete: delete an existing word and its translation.
    Rate: set the error rate for a specific word.
    Check: check for a word if exists

    """
    def __init__(self):
        self.connection = None
        self.create_connection()
        self.initialize_tables()

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect("dict.db")
            print("[INFO] connection to DB successful")
        except Error as e:
            print(f"[ERROR] error {e}")
        self.connection = conn

    def initialize_tables(self):
        create_tables = "CREATE TABLE IF NOT EXISTS dict (" \
                        "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                        "word TEXT," \
                        "translation," \
                        "rate INTEGER );"
        success = self.exec_query(create_tables)
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

    def check(self, word):
        pass

    def push(self, word, translation):
        create_word = f"""
        INSERT INTO 
            dict (word, translation, rate)
        VALUES
            ('{word}','{translation}',-1);
        """
        success = self.exec_query(create_word)
        if success == 0:
            print(f"[INFO] the word {word} and its translation {translation} are all set")

    def update(self, word, new_translation):
        select_query = f"SELECT translation FROM dict WHERE word = '{word}'"
        translations = self.exec_read_query(select_query)
        if len(translations) != 0:
            translations = new_translation[0]
        else:
            translations = ""
        translations += "," + new_translation
        update_query = f"""
        UPDATE
            dict
        SET
            translation = '{translations}'
        WHERE
            word = '{word}'
        """
        success = self.exec_query(update_query)
        if success == 0:
            print(f"[INFO] the word {word} has new translation {new_translation}")

    def delete(self, word):
        delete_query = f"DELETE FROM dict WHERE word = '{word}'"
        success = self.exec_query(delete_query)
        if success == 0:
            print(f"[INFO] The word {word} has been deleted")

    def rate(self, word, count):
        get_rate = f"SELECT rate FROM dict WHERE word='{word}'"
        rate = self.exec_read_query(get_rate)
        if len(rate) != 0:
            rate = rate[0][0]
        rate += count
        rate_update = f"""
        UPDATE
            dict 
        SET
            rate = {rate}
        WHERE
            word = '{word}'
        """
        success = self.exec_query(rate_update)
        if success == 0:
            print(f"[INFO] The rate for the word {word} is now {rate}")
