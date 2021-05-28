import sqlite3
from sqlite3 import Error


class DataBase:
    """
    API to represent the Database.
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
        :return: None
        """
        conn = None
        try:
            conn = sqlite3.connect(filename)
            print("[INFO] connection to DB successful")
        except Error as e:
            print(f"[ERROR] error {e}")
        self.connection = conn

    def initialize_tables(self):
        """
        Initialize tables in db.
        :return: None
        """

        persons_table = "CREATE TABLE IF NOT EXISTS persons (" \
                        "id INTEGER PRIMARY KEY AUTOINCREMENT," \
                        "name TEXT NOT NULL," \
                        "telegram_id INTEGER NOT NULL," \
                        "age INTEGER NOT NULL, " \
                        "gender INTEGER NOT NULL," \
                        "dict_index INTEGER NOT NULL );"

        scores_table = "CREATE TABLE IF NOT EXISTS scores (" \
                       "word_id INTEGER NOT NULL," \
                       "person_id INTEGER NOT NULL," \
                       "duration INTEGER NOT NULL," \
                       "failures INTEGER NOT NULL, " \
                       "total INTEGER NOT NULL, " \
                       "FOREIGN KEY (person_id) REFERENCES persons(id) );"

        success = self.exec_query(persons_table) + self.exec_query(scores_table)
        if success == 0:
            print("[INFO] Tables are all set")

    def exec_query(self, query):
        """
        Generic function to execute read query on db
        :param query: query to execute
        :return: list with the results; or empty list if there was no result
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            self.connection.commit()
            return 0
        except Error as e:
            print(f"[ERROR] The error {e} occurred")
            return 1

    def exec_read_query(self, query):
        """
        Generic function to execute read query on db
        :param query: query to execute
        :return: list with the results; or empty list if there was no result
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"[ERROR] The error {e} occurred")
            return []

    def check_for_person(self, conditions):
        """
        Check for person with given set of conditions
        :param conditions: dictionary
        :raise Exception if conditions are empty
        :return: True if person with give conditions exist; False otherwise
        """
        if not len(conditions.items()):
            raise Exception("No conditions to work with")
        conditions = " AND ".join([f"{str(key)}='{conditions.get(key)}'" for key in conditions.keys()])
        query = f"SELECT * FROM persons WHERE ({conditions})"
        result = self.exec_read_query(query)
        return len(result) != 0

    def add_new_person(self, name, telegram_id, gender, age):
        """
        Add new person to Database.
        set the new person's dict_index to 0
        :param name: name of the person
        :param telegram_id: telegram id of the telegram account
        :param gender: gender of person
        :param age: age of person
        :return: None
        """
        if self.check_for_person({'telegram_id': telegram_id}):
            return
        query = f"""INSERT INTO
                      persons (name, telegram_id, gender, age, dict_index)
                   VALUES
                       ('{name}', '{telegram_id}', '{gender}', '{age}', '{0}'); 
                """
        result = self.exec_query(query)
        if result == 0:
            print(f"[INFO] new person updated name : {name}, telegram_id : {telegram_id}")

