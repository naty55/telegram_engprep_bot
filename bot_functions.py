from time import sleep
from apis import db_api
from telegram import Bot, Message
from Person import Person
from util import get_ram_mem


def notify_all_users(message: str, bot: Bot) -> None:
    """
    Send Notification to all registered users;
    There is a telegram API limitation that only allow sending 30 messages
    in a minute so the function will take care of that too.
    :param message: message to send
    :param bot: The bot
    :return: None
    """

    name, image = get_ram_mem()
    message += "\n\n\n" + "Character-name: " + name

    counter = 0
    for _id in db_api.get_all_persons_id():
        try:
            counter += 1
            bot.send_photo(_id, photo=image, caption=message)
            if counter >= 28:
                sleep(60)
        except Exception as e:
            print(f"Couldn't send message for user {db_api.get_person_data(_id).get('name')}")
            print(e)


def send_message(text: str, bot: Bot, person: Person, interval: float = 0.01, animate: bool = False) -> Message:
    text = text.strip()
    if animate:
        str_to_send = text[0]
        message = bot.send_message(chat_id=person.id, text=str_to_send)
        for letter in text[1:]:
            str_to_send += letter
            if letter.isspace():
                continue
            message.edit_text(str_to_send)
            sleep(interval)
        return message

    return bot.send_message(chat_id=person, text=text)


def count_down(person: Person, bot: Bot, prefix: str = "", interval: float = 0.5) -> None:
    prefix += " "
    message = bot.send_message(chat_id=person.id, text=prefix + "10")
    for i in range(9, -1, -1):
        sleep(interval)
        text = prefix + str(i)
        message.edit_text(text)
    message.delete()
