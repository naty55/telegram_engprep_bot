import telegram
from telegram import Update, Bot, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from collections import defaultdict

from Person import Person

# CONSTANTS
gender_kb = [[InlineKeyboardButton('Male', callback_data='gender_male')],
             [InlineKeyboardButton('Female', callback_data='gender_female')],
             [InlineKeyboardButton('Other', callback_data='gender_other')]]
gender_markup = InlineKeyboardMarkup(gender_kb)

#
sessions = defaultdict(lambda: False)


def start_handler(update: Update, context: CallbackContext):
    person_id = update.effective_user.id
    start_session(person_id, update.effective_user.name)

    person = sessions.get(person_id)
    bot = context.bot
    bot.send_chat_action(chat_id=person.telegram_chat_id, action=telegram.ChatAction.TYPING)
    if not person.is_known:
        bot.send_message(chat_id=person_id, text="Welcome " + person.name + "\nUse /register command to register")
    else:
        bot.send_message(chat_id=person_id, text="Welcome back " + person.name)


def register_handler(update: Update, context: CallbackContext):
    person_id = update.effective_user.id
    start_session(person_id, update.effective_user.name)
    person = sessions.get(person_id)
    if person.is_known:
        context.bot.send_message(text="you are already registered", chat_id=person_id)
    else:
        context.bot.send_message(reply_markup=gender_markup, chat_id=person.telegram_chat_id, text="What's your gender")


def button_map_handler(update: Update, context: CallbackContext):
    update.callback_query.answer()
    query = update.callback_query
    answer = query.data
    if answer.startswith('gender_'):
        person = sessions.get(update.effective_user.id)
        person.touch()
        person.gender = answer.split('_')[1]
        query.delete_message()
        get_age(person)
    elif answer.startswith('age_'):
        pass


def conversation_map_handler(update: Update, context: CallbackContext):
    print(update.message.text)


def get_age(person: Person):
    pass


def start_session(person_id, name):
    """
    check if session already exist; if not create new session
    :param person_id: person's id
    :param name: person's name
    :return: None
    """
    if not sessions.get(person_id):
        person = Person(person_id, name)
        sessions[person_id] = person
