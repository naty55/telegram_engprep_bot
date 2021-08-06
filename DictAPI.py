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

    def get_question(self, range_=(0, -1), number_of_options=4, on_heb_words=False):
        a = range_[0]
        b = range_[1]
        if b < 0:
            b = len(self.rows) + b
        word_lang_idx = 1
        answer_lang_idx = 2
        if on_heb_words:
            word_lang_idx, answer_lang_idx = answer_lang_idx, word_lang_idx
        answer_index = random.randint(a, b)
        word = self.rows[answer_index][word_lang_idx]
        answer = self.rows[answer_index][answer_lang_idx]

        options = [answer]
        while len(options) < number_of_options:
            index = random.randint(0, len(self.rows) - 1)
            option = self.rows[index][answer_lang_idx]
            if option not in options:
                options.append(option)
        random.shuffle(options)
        answer = options.index(answer)
        return {'word': word,
                'answer': answer,
                'options': options}


