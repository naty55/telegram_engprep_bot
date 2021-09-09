from telegram import (Update,
                      InlineKeyboardButton,
                      InlineKeyboardMarkup,
                      Poll,
                      )
from telegram.error import BadRequest
from telegram.ext import (CommandHandler,
                          CallbackQueryHandler,
                          PollAnswerHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          )

from apis import dict_api, db_api, bot_logger, sessions, message_logger, ram_api
from Person import Person
from bot_decorators import basic_handler, registered_only
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


@basic_handler(CommandHandler, command='start')
def start_handler(person: Person, context: CallbackContext):
    if not person.is_known:
        context.bot.send_message(chat_id=person.id, text="Welcome " + person.name +
                                                         "\nUse /register command to register\n"
                                                         "Use /menu to get all options of this bot")
    else:
        context.bot.send_message(chat_id=person.id,
                                 text="Welcome back " + person.name + "\n"
                                                                      "Use /menu to get all options "
                                                                      "of this bot")


@basic_handler(CommandHandler, command='menu')
def menu_handler(person: Person, context: CallbackContext):
    text = ("/start start conversion with the bot\n"
            "/menu get all options of this bot\n"
            "/register register in order to use the bot\n"
            "/quiz_me quiz yourself (15 questions)\n"
            "/quiz_me_en quiz yourself on English words\n"
            "/quiz_me_he quiz yourself on Hebrew words\n"
            "/contact send message to the developer")
    context.bot.send_message(chat_id=person.id, text=text)


@basic_handler(CommandHandler, command='register')
def register_handler(person: Person, context: CallbackContext):
    if person.is_known:
        context.bot.send_message(text="you are already registered", chat_id=person.id)
    else:
        context.bot.send_message(reply_markup=gender_markup, chat_id=person.id, text="What's your gender")


@basic_handler(CommandHandler, 'contact')
@registered_only()
def contact_handler(person: Person, update: Update, context: CallbackContext):
    message = update.message.text[8:].strip()
    if message:
        message_logger.info("message form %s  id: %d : %s", person.name, person.id, message)
        context.bot.send_message(chat_id=person.id, text="Thanks for your message")
    else:
        context.bot.send_message(chat_id=person.id, text="Use /contact  <your message right here>")


@basic_handler(CallbackQueryHandler)
def button_map_handler(person: Person, update: Update, context: CallbackContext):
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
        context.bot.send_message(text="How old are you ? ", chat_id=person.id)

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
    elif answer.startswith('lang') and person.is_known:
        # Making sure person is known - not required but on the safe side
        on_heb_words = True if 'he' in answer else False
        start_quiz(person, context, on_heb_words)


@basic_handler(CommandHandler, command='quiz_me')
@registered_only()
def quiz_me_handler(person: Person, context: CallbackContext):
    context.bot.send_message(chat_id=person.id, reply_markup=choose_lang_button, text="Choose option: ")


@basic_handler(CommandHandler, command='quiz_me_en')
@registered_only(send_message=False)
def quiz_me_en_handler(person: Person, context: CallbackContext):
    start_quiz(person, context, False)


@basic_handler(CommandHandler, command='quiz_me_he')
@registered_only(send_message=False)
def quiz_me_he_handler(person: Person, context: CallbackContext):
    start_quiz(person, context, True)


@basic_handler(PollAnswerHandler)
@registered_only(send_message=False)
def quiz_handler(person: Person, update: Update, context: CallbackContext):
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


@basic_handler(MessageHandler, regex_filter=Filters.regex("^[1-9][0 -9]*$"))
def age_handler(person: Person, update: Update, context: CallbackContext):
    if person.interval_to_get_age_is_open:
        person.age = int(update.message.text)
        person.interval_to_get_age_is_open = False  # Close Interval the bot now will no longer get text messages
        person.save_person_data()  # DONE
        context.bot.send_message(text="Registration Completed\nUse /menu to see what this bot can do",
                                 chat_id=person.id)

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
    success_percentage = round(((15 - person.failed) / 15) * 100, 2)
    context.bot.send_message(chat_id=person.id, text=f"Your score is {success_percentage}")
    bot_logger.info("%s finished quiz with score %s id: %s", person.name, str(success_percentage), person.id)


def start_quiz(person: Person, context: CallbackContext, on_heb: bool):
    """
    This function assumes that person is registered - therefore this method should be called from
    handlers decorated with @registered_only
    :param person:
    :param context:
    :param on_heb:
    :return:
    """
    if person.is_on_quiz:
        return
    person.start_quiz(on_heb)
    quiz_person(person, context)
    bot_logger.info("%s started quiz id: %s", person.name, person.id)


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
            name, image = ram_api.get_character()
            message += "\n\n\n" + "Character-name: " + name
            bot.send_photo(_id, photo=image, caption=message)
        except Exception as e:
            print(f"Couldn't send message for user {db_api.get_person_data(_id).get('name')}")
            print(e)

