from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from dotenv import load_dotenv
from os import getenv
from typing import Dict, Callable
from dispatchers import dispatch_handlers, dispatch_callback_query


class Environment:
    def __init__(self, envs: Dict[str, str]):
        if not load_dotenv():
            raise RuntimeError("missing .env in cwd")

        self.__env: Dict[str, str] = {}

        for envname, envkey in envs.items():
            value: (str | None) = getenv(envkey)

            if value is not None:
                self.__env.update({envname: value})

    def __getitem__(self, item):
        return self.__env[item]


class Bot:
    def __init_env(self):
        self.__env: Environment = Environment({'token': 'BOT_TOKEN',
                                               'passwd': 'BOT_PASSWD',
                                               'db_name': 'BOT_DB_NAME',
                                               'db_admin': 'BOT_DB_ADMIN',
                                               'db_tables': 'BOT_DB_TABLES',
                                               'group': 'BOT_GROUP',
                                               'threads': 'BOT_THREADS'})

    def __init__(self):
        self.__init_env()

        self._bot = TeleBot(token=self.__env['token'],
                            parse_mode='None',
                            num_threads=int(self.__env['threads']))

    def get_config(self) -> Environment:
        return self.__env

    def start(self):
        self._bot.infinity_polling(skip_pending=True)

    def register_message_dispatcher(self, dispatcher: Callable[[Message, TeleBot], None]):
        # registers new message dispatcher
        self._bot.register_message_handler(callback=dispatcher, pass_bot=True)

    def register_callback_query_dispatcher(self, dispatcher: Callable[[CallbackQuery, TeleBot], None]):
        # registers new callback query dispatcher
        self._bot.register_callback_query_handler(callback=dispatcher, func=lambda call: True, pass_bot=True)


if __name__ == "__main__":
    bot = Bot()
    bot.register_message_dispatcher(dispatch_handlers)
    bot.register_callback_query_dispatcher(dispatch_callback_query)
    bot.start()
