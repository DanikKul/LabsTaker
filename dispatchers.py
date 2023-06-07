from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from handle.user import user_handlers, user_handlers_names, user_query_handlers, user_query_handlers_names
from handle.su import admin_handlers, admin_handlers_names, admin_query_handlers, admin_query_handlers_names


def dispatch_handlers(message: Message, bot: TeleBot):

    req = message.text.split(' ')
    req[0] = req[0][1:]

    for idx, command in enumerate(user_handlers_names):
        if command == req[0]:
            user_handlers[idx](message, bot)
            break

    for idx, command in enumerate(admin_handlers_names):
        if 'admin_' + command == req[0]:
            admin_handlers[idx](message, bot)
            break


def dispatch_callback_query(call: CallbackQuery, bot: TeleBot):

    for idx, command in enumerate(user_query_handlers_names):
        if call.data.startswith(command):
            user_query_handlers[idx](call, bot)
            break

    for idx, command in enumerate(admin_query_handlers_names):
        if call.data.startswith(command):
            admin_query_handlers[idx](call, bot)
            break

