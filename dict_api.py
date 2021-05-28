import csv


class DictAPI:

    """
    DictApi lets you control the dictionary (csv file) with more ease
    """

    def __init__(self, dictfile):
        self.csvfile = open(dictfile, 'r', encoding='utf-8', newline='')
        self.reader = csv.reader(self.csvfile, delimiter=',')
        self.rows = list(self.reader)

    def get_words(self, start_index, amount):
        return self.rows[start_index:start_index + amount]

    def close(self):
        self.csvfile.close()
