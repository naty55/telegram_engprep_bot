import csv
import random

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

    def get_question(self, range_=(0, -1), number_of_options=4):
        a = range_[0]
        b = range_[1]
        if b < 0:
            b = len(self.rows) + b

        answer_index = random.randint(a, b)
        word = self.rows[answer_index][2]
        answer = self.rows[answer_index][1]

        options = [answer]
        while len(options) < number_of_options:
            index = random.randint(0, len(self.rows) - 1)
            option = self.rows[index][1]
            if option not in options:
                options.append(option)
        random.shuffle(options)
        answer = options.index(answer)
        return {'word': word,
                'answer': answer,
                'options': options}


