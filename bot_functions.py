from telegram import (Update,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      Poll,
                      ChatAction
                      )
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from apis import dict_api, db_api, bot_logger
from Person import Person
from SessionsDict import SessionsDict
from threading import Thread
from time import sleep, time

# CONSTANTS
gender_kb = ([InlineKeyboardButton('Male', callback_data='gender_male')],
             [InlineKeyboardButton('Female', callback_data='gender_female')],
             [InlineKeyboardButton('Other', callback_data='gender_other')])
next_kb = ((InlineKeyboardButton('Finish Quiz', callback_data='finish_button'),
            InlineKeyboardButton('Next', callback_data='next')),)
lang_kb = ((InlineKeyboardButton('Quiz on English words', callback_data='lang_en_button'),),
           (InlineKeyboardButton('Quiz on Hebrew words', callback_data='lang_he_button'),))

next_button = InlineKeyboardMarkup(next_kb)
gender_markup = InlineKeyboardMarkup(gender_kb)
choose_lang_button = InlineKeyboardMarkup(lang_kb)
#
sessions = SessionsDict(lambda: False)


def start_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)

    context.bot.send_chat_action(chat_id=person.id, action=ChatAction.TYPING)
    if not person.is_known:
        context.bot.send_message(chat_id=person_id, text="Welcome " + person.name +
                                                         "\nUse /register command to register\n"
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
        context.bot.send_message(reply_markup=gender_markup, chat_id=person.id, text="What's your gender")


def button_map_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    update.callback_query.answer()
    query = update.callback_query
    answer = query.data

    try:
        query.delete_message()
    except BadRequest:
        pass  # Ignore case; message couldn't be deleted

    if answer.startswith('gender_'):
        person.gender = answer.split('_')[1]
        person.interval_to_get_age_is_open = True
        context.bot.send_message(text="How old are you ? ", chat_id=person_id)

    elif answer.startswith('next') or answer.startswith('finish'):
        try:
            context.bot_data.pop(query.message.message_id).delete()
        except KeyError:
            pass  # Ignore case when the poll is not registered in bot_data
        else:
            if answer.startswith('next'):
                quiz_person(person, context)
            else:
                finish_quiz(person, context)
    elif answer.startswith('lang'):
        on_heb_words = True if 'he' in answer else False
        person.start_quiz(on_heb_words)
        quiz_person(person, context)

        bot_logger.info("%s started quiz id: %s", person.name, person.id)


def quiz_me_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    if not person.is_known:
        context.bot.send_message(chat_id=person_id, text="please use /register to register first")
    else:
        if person.is_on_quiz:
            # To be decided
            # context.bot.send_message(chat_id=person.id, reply_markup=next_button,
            #                          text="You have to finish you quiz first")
            return
        context.bot.send_message(chat_id=person_id, reply_markup=choose_lang_button, text="Choose option: ")


def quiz_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    user_answer = update.poll_answer.option_ids[0]
    try:
        poll_correct_answer = context.bot_data.pop(update.poll_answer.poll_id)
    except KeyError:
        pass  # Ignore case he poll is not registered
    else:
        if poll_correct_answer == user_answer:
            person.failed -= 1
        else:
            pass


def age_handler(update: Update, context: CallbackContext):
    person, person_id = start_session(update.effective_user.id, update.effective_user.name)
    if person.interval_to_get_age_is_open:
        person.age = int(update.message.text)
        person.interval_to_get_age_is_open = False  # Close Interval the bot now will no longer get text messages
        person.save_person_data()  # DONE
        context.bot.send_message(text="Registration Completed\nUse /menu to see what this bot can do",
                                 chat_id=person_id)

        bot_logger.info("%s registered id: %s", person.name, person.id)


def quiz_person(person: Person, context: CallbackContext):
    if person.left_questions > 0:
        question = dict_api.get_question(on_heb_words=person.quiz_on_heb_words)
        word = question['word']
        answer = question['answer']
        options = question['options']
        q = f"What is the translation of the word '{word}'"
        poll_message = context.bot.send_poll(chat_id=person.id, question=q, options=options,
                                             type=Poll.QUIZ,
                                             correct_option_id=answer, is_anonymous=False)
        button_message = context.bot.send_message(chat_id=person.id, reply_markup=next_button,
                                                  text="_" * 45)
        context.bot_data[button_message.message_id] = poll_message
        context.bot_data[poll_message.poll.id] = poll_message.poll.correct_option_id
        person.left_questions -= 1
    else:
        finish_quiz(person, context)


def finish_quiz(person: Person, context: CallbackContext):
    person.init_quiz()
    success_percentage = round((15 - person.failed)/ 15 , 2) * 100
    context.bot.send_message(chat_id=person.id, text=f"Your score is {success_percentage}")
    bot_logger.info("%s finished quiz with score %s id: %s", person.name, str(success_percentage), person.id)


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
        bot_logger.info("%s started session with the bot id: %s", person.name, person.id)

    return person, person_id


def clean_old_sessions():
    interval = 30 * 60
    while True:
        sleep(interval)
        for i in list(sessions.keys()):
            if time() - sessions[i].time > interval:
                person = sessions.pop(i)
                bot_logger.info("%s session expired id: %s", person.name, person.id)


def notify_all_users(message, bot):
    """
    Send message to all users that are in the db
    :param message: message to send
    :param bot: The bot
    :return: None
    """
    for _id in db_api.get_all_persons_id():
        try:
            bot.send_message(_id, message)
        except Exception as e:
            print(f"Couldn't send message for user {db_api.get_person_data(_id).get('name')}")
            print(e)


Thread(target=clean_old_sessions).start()
