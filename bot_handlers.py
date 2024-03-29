from telegram import Update, Poll
from telegram.error import BadRequest
from telegram.ext import (CommandHandler,
                          CallbackQueryHandler,
                          PollAnswerHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          )
from telegram_objects import choose_lang_button_markup, next_button_markup, gender_markup, compete_markup_factory, rematch_markup_factory
from apis import dict_api, bot_logger, sessions, message_logger, config
from bot_functions import send_message, count_down
from Person import Person
from bot_decorators import basic_handler, registered_only
from time import time
from threading import Thread


@basic_handler(CommandHandler, command='start')
def start_handler(person: Person, context: CallbackContext) -> None:
    """
    Start Handler - Greet the user and instruct the user how to use the bot
    :param person: person
    :param context: callback context
    :return: None
    """
    if not person.is_known:
        context.bot.send_message(chat_id=person.id,
                                 text=f"Welcome {person.name}\n"
                                      "Use /register command to register\n"
                                      "Use /menu to get all options of this bot")
    else:
        context.bot.send_message(chat_id=person.id,
                                 text=f"Welcome back {person.name}\n"
                                      "Use /menu to get all options "
                                      "of this bot")


@basic_handler(CommandHandler, command='bot_status')
def status_handler(person: Person, context: CallbackContext) -> None:
    """
    Status Handler - send bot status to the user, this is an admins' only command
    :param person: person
    :param context: callbackContext
    :return: None
    """
    if person.id in config['admins']:
        text = ("Bot is Up\n\n"
                "Open sessions:\n"
                ) + "\n".join((person.name for person in sessions.values()))
        context.bot.send_message(chat_id=person.id, text=text)


@basic_handler(CommandHandler, command='menu')
def menu_handler(person: Person, context: CallbackContext) -> None:
    """
    Menu Handler - send the menu to the user
    :param person: person
    :param context: callbackContext
    :return: None
    """
    text = ("/start start conversion with the bot\n"
            "/menu get all options of this bot\n"
            "/register register in order to use the bot\n"
            "/quiz_me quiz yourself (15 questions)\n"
            "/quiz_me_en quiz yourself on English words\n"
            "/quiz_me_he quiz yourself on Hebrew words\n"
            "/contact send message to the developer\n"
            "/compete compete against friend")
    context.bot.send_message(chat_id=person.id, text=text)


@basic_handler(CommandHandler, command='register')
def register_handler(person: Person, context: CallbackContext) -> None:
    """
    Register Handler - let  the user start registration process
    :param person: person
    :param context: callbackContext
    :return: None
    """
    if person.is_known:
        context.bot.send_message(text="you are already registered", chat_id=person.id)
    else:
        context.bot.send_message(reply_markup=gender_markup, chat_id=person.id, text="What's your gender")


@basic_handler(CommandHandler, 'contact')
@registered_only()
def contact_handler(person: Person, update: Update, context: CallbackContext) -> None:
    """
    Contact Handler - let the user contact and send feedback to the developer
    :param person: perosn
    :param update: Update
    :param context: callbackContext
    :return: None
    """
    message = update.message.text[8:].strip()
    if message:
        message_logger.info("message form %s  id: %d : %s", person.name, person.id, message)
        context.bot.send_message(chat_id=person.id, text="Thanks for your message")
    else:
        context.bot.send_message(chat_id=person.id, text="Use /contact  <your message>")


@basic_handler(CallbackQueryHandler)
def button_map_handler(person: Person, update: Update, context: CallbackContext) -> None:
    """
    Button Handler - This handler handle every type of button pressing event
    :param person: person
    :param update: Update
    :param context: callbackContext
    :return:
    """
    update.callback_query.answer()
    query = update.callback_query
    answer = query.data
    try:
        query.delete_message()
    except BadRequest:
        pass  # Ignore case; message couldn't be deleted

    data = answer.split('_')
    req_type = data[0]
    if req_type == 'gender':
        person.gender = data[1]
        person.interval_to_get_age_is_open = True
        context.bot.send_message(text="How old are you ? ", chat_id=person.id)

    elif req_type == 'quiz':
        try:
            context.bot_data.pop(update.callback_query.message.poll.id)
        except KeyError:
            pass  # Ignore
        finally:
            if answer.endswith('next'):
                quiz_person(person, context)
            else:
                finish_quiz(person, context)
    elif req_type == 'lang' and person.is_known:
        # Making sure person is known - not required but on the safe side
        on_heb_words = True if 'he' in data else False
        start_quiz(person, context, on_heb_words)

    elif req_type == 'compete' and person.is_known:
        _, accepted, offering_person_id, offer_time = data
        if time() - float(offer_time) > 620:
            print("Offer expired")
            return
        if accepted == "accept" and not person.is_busy():
            person1 = sessions.get(int(offering_person_id))
            start_competition(person, person1, context)

    elif req_type == 'rematch':
        another_user_id = data[1]
        compete_person(person, context, another_user_id)


@basic_handler(CommandHandler, command='quiz_me')
@registered_only()
def quiz_me_handler(person: Person, context: CallbackContext):
    context.bot.send_message(chat_id=person.id, reply_markup=choose_lang_button_markup, text="Choose an option: ")


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


@basic_handler(CommandHandler, 'compete')
@registered_only()
def compete_handler(person: Person, update: Update, context: CallbackContext):
    try:
        another_person_id = update.message.text[8:].strip()
    except AttributeError:
        pass
    else:
        if another_person_id.isalnum():
            compete_person(person, context, another_person_id)


def compete_person(person: Person, context: CallbackContext, another_person_id):
    if person.is_busy() or str(person.id) == str(another_person_id):
        return
    try:
        another_person = sessions.get(int(another_person_id))
        if another_person:
            if another_person.is_busy():
                context.bot.send_message(chat_id=person.id,
                                         text=f"The person {another_person_id} is busy right now "
                                              "Try in 10 minutes again")

        context.bot.send_message(chat_id=another_person_id,
                                 reply_markup=compete_markup_factory(person.id, person.time),
                                 text=f"You are invited to a competition with {person.name}")
    except BadRequest:
        context.bot.send_message(chat_id=person.id,
                                 text="Couldn't find your friend,"
                                      "ask him to start conversation with the bot "
                                      "{@english_prep_bot}"
                                      "or check his id again")
    else:
        context.bot.send_message(chat_id=person.id,
                                 text=f"Invitation sent to {another_person_id}, "
                                      "and it will expire in 10 minutes from now")


def quiz_person(person: Person, context: CallbackContext):
    open_period = None
    if person.is_on_competition:
        open_period = 8
    if person.left_questions > 0:
        question = dict_api.get_question(on_heb_words=person.quiz_on_heb_words)
        word, word_id, answer, options = question['word'], question['word_id'], question['answer'], question['options']
        q = f"What is the translation of the word '{word}'"
        poll_message = context.bot.send_poll(chat_id=person.id,
                                             question=q,
                                             options=options,
                                             type=Poll.QUIZ,
                                             correct_option_id=answer,
                                             is_anonymous=False,
                                             reply_markup=next_button_markup,
                                             open_period=open_period
                                             )
        context.bot_data[poll_message.poll.id] = poll_message.poll.correct_option_id
        person.left_questions -= 1
    else:
        finish_quiz(person, context)


def finish_quiz(person: Person, context: CallbackContext):
    if person.is_on_competition:
        return finish_competition(person, context)
    send_message(f"Your score is {person.get_score()}", context.bot, person, animate=True)
    bot_logger.info("%s finished quiz with score %s id: %s", person.name, person.get_score(), person.id)
    person.init_quiz()


def start_quiz(person: Person, context: CallbackContext, on_heb=False, mode='quiz', against=None):
    """
    This function assumes that person is registered - therefore this method should be called from
    handlers decorated with @registered_only
    :param against:
    :param mode:
    :param person:
    :param context:
    :param on_heb:
    :return:
    """
    if against is None and mode == 'compete':
        raise Exception("got 'compete' mode but didn't got the opponent person")

    if person.is_busy():
        return
    if mode == 'quiz':
        person.start_quiz(on_heb)
        bot_logger.info("%s started quiz id: %s", person.name, person.id)
    elif mode == 'compete':
        person.start_competition(against)

    quiz_person(person, context)


def start_competition(person1, person2, context):
    t1 = Thread(target=count_down, args=(person1, context.bot, "Starting in"))
    t2 = Thread(target=count_down, args=(person2, context.bot, "Starting in"))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    start_quiz(person1, context, mode='compete', against=person2)
    start_quiz(person2, context, mode='compete', against=person1)


def finish_competition(person: Person, context: CallbackContext):
    if not person.against.finished_competition:
        send_message("Waiting for opponent to finish...", context.bot, person, animate=True)
        person.finish_competition()
    else:
        score = person.get_score()
        score1 = person.against.get_score()
        person_message = "Congrats, You won 🥳"
        person1_message = "Maybe next time, You lost 😔"
        if score1 > score:
            person1_message, person_message = person_message, person1_message
        elif score == score1:
            person1_message = person_message = "it's a draw"

        context.bot.send_message(chat_id=person.id,
                                 text=person_message,
                                 reply_markup=rematch_markup_factory(person.against.id))
        context.bot.send_message(chat_id=person.against.id,
                                 text=person1_message,
                                 reply_markup=rematch_markup_factory(person.id))
        person.against.init_competition()
        person.init_competition()


