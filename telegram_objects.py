from telegram import InlineKeyboardButton, InlineKeyboardMarkup

gender_kb = ([InlineKeyboardButton('Male', callback_data='gender_male')],
             [InlineKeyboardButton('Female', callback_data='gender_female')],
             [InlineKeyboardButton('Other', callback_data='gender_other')])
next_kb = ((InlineKeyboardButton('Finish Quiz', callback_data='finish_button'),
            InlineKeyboardButton('Next', callback_data='next')),)
lang_kb = ((InlineKeyboardButton('Quiz on English words', callback_data='lang_en_button'),),
           (InlineKeyboardButton('Quiz on Hebrew words', callback_data='lang_he_button'),))
compete_kb = ((InlineKeyboardButton('Decline', callback_data='compete_decline'),),
              (InlineKeyboardButton('Accept', callback_data='compete_accept'),))

next_button = InlineKeyboardMarkup(next_kb)
gender_markup = InlineKeyboardMarkup(gender_kb)
choose_lang_button = InlineKeyboardMarkup(lang_kb)
compete_markup = InlineKeyboardMarkup(compete_kb)
