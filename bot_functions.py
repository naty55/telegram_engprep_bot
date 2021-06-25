import time

import telegram
from telegram import Update, Bot, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from Person import Person

# CONSTANTS
gender_kb = [[InlineKeyboardButton('Male', callback_data='gender_male')],
             [InlineKeyboardButton('Female', callback_data='gender_female')],
             [InlineKeyboardButton('Other', callback_data='gender_other')]]
gender_markup = InlineKeyboardMarkup(gender_kb)

#
persons = {}


def start_handler(update: Update, context: CallbackContext):
    person = Person(update.effective_user.id, update.effective_user.name)
    persons[person.telegram_chat_id] = person
    bot = context.bot
    bot.send_chat_action(chat_id=person.telegram_chat_id, action=telegram.ChatAction.TYPING)
    if not person.is_known:
        register_person(bot, update, person)
    else:
        bot.send_message(chat_id=person.telegram_chat_id, text="Welcome back " + person.name)


def register_person(bot: Bot, update: Update, person: Person):
    bot.send_message(reply_markup=gender_markup, chat_id=person.telegram_chat_id, text="What's you gender")


def welcome_person(bot: Bot, person: Person):
    person_id = person.telegram_chat_id
    print(person_id)
    bot.send_message(chat_id=person_id, text="Welcome " + str(person_id))


def button_map_handler(update: Update, context: CallbackContext):
    update.callback_query.answer()
    query = update.callback_query
    answer = query.data
    if answer.startswith('gender_'):
        person = persons.get(update.effective_user.id)
        person.gender = answer.split('_')[1]
        print(person.gender)
        query.delete_message()
        pass

def get_gender():
    pass