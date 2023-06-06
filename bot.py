import telebot as tt
from configuration import get_config
import time as tm
import dotenv as env
from database import *
from handlers import user
from handlers import su
# from handlers.user import help_hd, su_hd, ban_hd, edit_hd, list_hd, take_hd, time_hd, login_hd, start_hd, cancel_hd, queues_hd, status_hd, exchange_hd
# from handlers.su import admin_kick_hd, admin_users_hd, admin_edit_hd, admin_list_hd, admin_time_hd, admin_change_hd, admin_create_hd, admin_delete_hd, admin_remove_hd

# ___________________________________________________UTILS____________________________________________________________ #

spams = {}
msgs = 4
maxim = 1
ban = 300

# _______________________________________________CONFIGURATION________________________________________________________ #


env.load_dotenv()

config = get_config()

bot = tt.TeleBot(token=config['token'], parse_mode=None, num_threads=6)

session = database_connect(config['db_name'])

db_init_admin(session)
tables_database_init(session)
db_init_users(session)
close_connection(session)


def is_spam(user_id: int) -> bool:
    try:
        usr = spams[user_id]
        usr["messages"] += 1
    except Exception as e:
        spams[user_id] = {"next_time": int(tm.time()) + maxim, "messages": 1, "banned": 0}
        usr = spams[user_id]
    if usr["banned"] >= int(tm.time()):
        return True
    else:
        if usr["next_time"] >= int(tm.time()):
            if usr["messages"] >= msgs:
                spams[user_id]["banned"] = tm.time() + ban
                text = """Хотел поспамить? Получай бан на {} минут""".format(ban / 60)
                bot.send_message(user_id, text)
                return True
        else:
            spams[user_id]["messages"] = 1
            spams[user_id]["next_time"] = int(tm.time()) + maxim
    return False


def is_logged(user_id: int) -> bool:
    try:
        session = database_connect(config['db_name'])
        users = get_all_users(session)
        for user in users:
            if str(user[1]) == str(user_id):
                return True
        close_connection(session)
        bot.send_message(user_id, "Выполните вход в систему /login")
    except Exception as e:
        print("FUNC: callback_login_handler ERR:", e)
    return False



def message_filter(tg_id: int) -> bool:
    if is_spam(tg_id):
        return False

    if not is_logged(tg_id):
        return False

    return True


# @bot.message_handler()
# def message_hd(message: tt.types.Message):
#     message_filter(message.chat.id)


def start():
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    user.register_user_handlers(bot)
    su.register_admin_handlers(bot)
    start()