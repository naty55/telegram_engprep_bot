from functools import wraps
from telegram import ChatAction
from apis import bot_logger, sessions
from Person import Person

#  Should be refactored to remove repetition

default_not_known_message = "You are not registered please use /register to register first"


def basic_handler_wrapper(func):
    @wraps(func)
    def wrapper(update, context):
        person = _start_session(update.effective_user.id, update.effective_user.name)
        context.bot.send_chat_action(chat_id=person.id, action=ChatAction.TYPING)
        func(person, context)

    return wrapper


def update_handler_wrapper(func):
    @wraps(func)
    def wrapper(update, context):
        person = _start_session(update.effective_user.id, update.effective_user.name)
        context.bot.send_chat_action(chat_id=person.id, action=ChatAction.TYPING)
        func(person, update, context)
    return wrapper


def registered_only(not_known_message=default_not_known_message):
    def decorator(func):
        @wraps(func)
        def wrapper(person, context):
            if person.is_known:
                func(person, context)
            else:
                try:
                    context.bot.send_message(chat_id=person.id, text=not_known_message)
                except:
                    print(f"couldn't send message to {person.id} - {person.name}")
        return wrapper
    return decorator


def update_registered_only(not_known_message=default_not_known_message):
    def decorator(func):
        @wraps(func)
        def wrapper(person, update, context):
            if person.is_known:
                func(person, update, context)
            else:
                try:
                    context.bot.send_message(chat_id=person.id, text=not_known_message)
                except:
                    print(f"couldn't send message to {person.id} - {person.name}")
        return wrapper
    return decorator


def _start_session(_id, _name):
    """
        check if session already exist; if not create new session
        :param _id: person's id
        :param _name: person's name
        :return: Person
    """
    person = sessions.get(_id)
    if not person:
        person = Person(_id, _name)
        sessions[person.id] = person
        bot_logger.info("%s started session with the bot id: %s", person.name, person.id)

    return person
