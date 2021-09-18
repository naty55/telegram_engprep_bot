from telegram import InlineKeyboardButton, InlineKeyboardMarkup

gender_kb = ([InlineKeyboardButton('Male', callback_data='gender_male')],
             [InlineKeyboardButton('Female', callback_data='gender_female')],
             [InlineKeyboardButton('Other', callback_data='gender_other')])
next_kb = ((InlineKeyboardButton('Finish Quiz', callback_data='finish_button'),
            InlineKeyboardButton('Next', callback_data='next')),)
lang_kb = ((InlineKeyboardButton('Quiz on English words', callback_data='lang_en_button'),),
           (InlineKeyboardButton('Quiz on Hebrew words', callback_data='lang_he_button'),))
next_button_markup = InlineKeyboardMarkup(next_kb)
gender_markup = InlineKeyboardMarkup(gender_kb)
choose_lang_button_markup = InlineKeyboardMarkup(lang_kb)

def compete_markup_factory(person_id, time):
    compete_kb = ((InlineKeyboardButton('Decline', callback_data=f'compete_decline_{person_id}_{time}'),),
                  (InlineKeyboardButton('Accept', callback_data=f'compete_accept_{person_id}_{time}'),))
    return InlineKeyboardMarkup(compete_kb)