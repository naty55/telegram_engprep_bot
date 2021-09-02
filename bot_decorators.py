from functools import wraps
from inspect import signature
from telegram import ChatAction
from apis import bot_logger, sessions, updater
from Person import Person

#  Should be refactored to remove repetition

default_not_known_message = "You are not registered please use /register to register first"


def basic_handler_wrapper(handler, command=None, regex_filter=None):
    def decorator(func):
        arguments_count = len(signature(func).parameters.keys())

        def wrapper(update, context):
            person = _start_session(update.effective_user.id, update.effective_user.name)
            context.bot.send_chat_action(chat_id=person.id, action=ChatAction.TYPING)
            if arguments_count == 2:
                func(person, context)
            else:
                func(person, update, context)

        handler_name = handler.__name__
        if handler_name == 'CommandHandler':
            updater.dispatcher.add_handler(handler(command, wrapper))
        elif handler_name == 'CallbackQueryHandler':
            updater.dispatcher.add_handler(handler(wrapper))
        elif handler_name == 'PollAnswerHandler':
            updater.dispatcher.add_handler(handler(wrapper, pass_user_data=True, pass_chat_data=True))
        elif handler_name == 'MessageHandler':
            updater.dispatcher.add_handler(handler(regex_filter, wrapper))

        return func
    return decorator


def registered_only(not_known_message=default_not_known_message, send_message=True):
    def decorator(func):
        arguments_count = len(signature(func).parameters.keys())
        if arguments_count == 2:

            @wraps(func)
            def wrapper(person, context):
                if person.is_known:
                    func(person, context)
                elif send_message:
                    try:
                        context.bot.send_message(chat_id=person.id, text=not_known_message)
                    except:
                        print(f"couldn't send message to {person.id} - {person.name}")

            return wrapper

        @wraps(func)
        def wrapper(person, update, context):
            if person.is_known:
                func(person, update, context)
            elif send_message:
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
