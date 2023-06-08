from typing import Callable
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from handle.user import user_handlers, user_handlers_names, user_query_handlers, user_query_handlers_names
from handle.su import admin_handlers, admin_handlers_names, admin_query_handlers, admin_query_handlers_names
from environment import Environment
from database import Session, database_connect
from middleware import Middleware


class Dispatch:
    def __init__(self, env: Environment):
        self.__env: Environment = env
        self.middleware = Middleware()

    def dispatch_handlers(self) -> Callable[[Message, TeleBot], None]:

        def _func(message: Message, bot: TeleBot):

            req = message.text.split(' ')
            req[0] = req[0][1:]

            if self.middleware.is_spam(bot, message.chat.id) and req[0] != 'ban':
                return

            session: Session = database_connect(self.__env['db_name'])

            if not self.middleware.is_logged(bot, session, message.chat.id) and req[0] != 'login':
                return

            for idx, command in enumerate(user_handlers_names):
                if command == req[0]:
                    if command == 'ban':
                        user_handlers[idx](message, bot, session, self.middleware, self.__env)
                    else:
                        user_handlers[idx](message, bot, session, self.__env)
                    break

            for idx, command in enumerate(admin_handlers_names):
                if 'admin_' + command == req[0]:
                    if self.middleware.is_admin(bot, session, message.chat.id):
                        admin_handlers[idx](message, bot, session)
                        break

        return _func

    def dispatch_callback_query(self) -> Callable[[CallbackQuery, TeleBot], None]:

        def _func(call: CallbackQuery, bot: TeleBot):

            if self.middleware.is_spam(bot, call.message.chat.id):
                return

            session = database_connect(self.__env['db_name'])

            if not self.middleware.is_logged(bot, session, call.message.chat.id):
                return

            for idx, command in enumerate(user_query_handlers_names):
                if call.data.startswith(command):
                    user_query_handlers[idx](call, bot, session, self.__env)
                    break

            for idx, command in enumerate(admin_query_handlers_names):
                if call.data.startswith(command):
                    if self.middleware.is_admin(bot, session, call.message.chat.id):
                        admin_query_handlers[idx](call, bot, session)
                        break

        return _func
