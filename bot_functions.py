import telegram
from telegram import Update, Bot, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, Poll, Message
from telegram.ext import CallbackContext
from time import sleep
from apis import dict_api
from Person import Person
from SessionsDict import SessionsDict

# CONSTANTS
gender_kb = [[InlineKeyboardButton('Male', callback_data='gender_male')],
             [InlineKeyboardButton('Female', callback_data='gender_female')],
             [InlineKeyboardButton('Other', callback_data='gender_other')]]
gender_markup = InlineKeyboardMarkup(gender_kb)

next_button = InlineKeyboardMarkup(((InlineKeyboardButton('Next', callback_data='next_button'),),))
#
sessions = SessionsDict(lambda: False)


def start_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)

    context.bot.send_chat_action(chat_id=person.telegram_chat_id, action=telegram.ChatAction.TYPING)
    if not person.is_known:
        context.bot.send_message(chat_id=person_id, text="Welcome " + person.name + "\nUse /register command to register\n"
                                                                            "Use /menu to get all options of this bot")
    else:
        context.bot.send_message(chat_id=person_id, text="Welcome back " + person.name + "\n"
                                                                                 "Use /menu to get all options "
                                                                                 "of this bot")


def menu_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    text = "/start start conversion with the bot\n" \
           "/menu get all options of this bot\n" \
           "/register register in order to use the bot\n" \
           "/quiz_me quiz yourself (15 questions)"
    context.bot.send_message(chat_id=person_id, text=text)


def register_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    if person.is_known:
        context.bot.send_message(text="you are already registered", chat_id=person_id)
    else:
        context.bot.send_message(reply_markup=gender_markup, chat_id=person.telegram_chat_id, text="What's your gender")


def button_map_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    update.callback_query.answer()
    query = update.callback_query
    answer = query.data

    if answer.startswith('gender_'):
        person.gender = answer.split('_')[1]
        person.interval_to_get_age_is_open = True
        context.bot.send_message(text="How old are you ? ", chat_id=person_id)

    elif answer.startswith('next'):
        try:
            context.bot_data.pop(query.message.message_id).delete()
        except KeyError:
            pass  # Ignore case when the poll is not registered in bot_data
        else:
            quiz_person(person, context)

    query.delete_message()


def quiz_me_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    if not person.is_known:
        context.bot.send_message(chat_id=person_id, text="please use /register to register first")
    else:
        person.is_on_quiz = True
        person.left_questions = 15
        quiz_person(person, context)


def quiz_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    user_answer = update.poll_answer.option_ids[0]
    try:
        poll_correct_answer = context.bot_data.pop(update.poll_answer.poll_id)
    except KeyError:
        pass  # Ignore case he poll is not registered
    else:
        if poll_correct_answer == user_answer:
            print("WW")
        else:
            print("HH")


def age_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    if person.interval_to_get_age_is_open:
        person.age = int(update.message.text)
        person.interval_to_get_age_is_open = False  # Close Interval the bot now will no longer get text messages
        person.save_person_data()  # DONE
        context.bot.send_message(text="Registration Completed\nUse /menu to see what this bot can do", chat_id=person_id)


def quiz_person(person: Person, context: CallbackContext):
    if person.left_questions > 0:
        question = dict_api.get_question()
        word = question['word']
        answer = question['answer']
        options = question['options']
        q = f"What is the translation of the word '{word}'"
        poll_message = context.bot.send_poll(chat_id=person.telegram_chat_id, question=q, options=options, type=Poll.QUIZ,
                                        correct_option_id=answer, is_anonymous=False)
        button_message = context.bot.send_message(chat_id=person.telegram_chat_id,  reply_markup=next_button, text="_" * 30)
        context.bot_data[button_message.message_id] = poll_message
        context.bot_data[poll_message.poll.id] = poll_message.poll.correct_option_id
        person.left_questions -= 1
    else:
        context.bot.send_message(text="Good Job", chat_id=person.telegram_chat_id)


def start_session(person_id, name):
    """
    check if session already exist; if not create new session
    :param person_id: person's id
    :param name: person's name
    :return: None
    """
    person = sessions.get(person_id)
    if not person:
        person = Person(person_id, name)
        sessions[person_id] = person
    return person, person_id
