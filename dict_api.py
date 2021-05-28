import csv

class DictAPI:

    def __init__(self, dictfile):
        self.dictfile = csv.reader(open(dictfile, encoding='utf-8'))


    def get_words(self, start_index, amount):
        pass
